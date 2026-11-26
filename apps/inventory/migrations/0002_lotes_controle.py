import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from django.utils import timezone
from django.db.models import Q


def migrar_saldos_legados(apps, schema_editor):
    Produto = apps.get_model("catalog", "Produto")
    Lote = apps.get_model("inventory", "Lote")
    Movimentacao = apps.get_model("inventory", "MovimentacaoEstoque")
    banco = schema_editor.connection.alias
    hoje = timezone.localdate()
    for produto in Produto.objects.using(banco).all().iterator():
        saldo = produto.estoque or 0
        if saldo < 0:
            raise RuntimeError(f"Produto {produto.pk} possui estoque negativo ({saldo}); corrija o saldo antes de migrar para lotes.")
        if saldo > 0:
            observacao = "Saldo existente convertido na implantação do controle por lotes. Data registrada é a data da conversão; validade histórica desconhecida."
            lote = Lote.objects.using(banco).create(
                produto_id=produto.pk,
                codigo=f"LEGADO-{produto.pk}",
                quantidade_inicial=saldo,
                quantidade_disponivel=saldo,
                data_entrada=hoje,
                data_validade=None,
                custo_unitario=produto.custo_aquisicao or 0,
                observacao=observacao,
                legado=True,
            )
            Movimentacao.objects.using(banco).create(
                produto_id=produto.pk, lote_id=lote.pk, tipo="ajuste", quantidade=saldo,
                saldo_anterior=0, saldo_posterior=saldo, referencia="MIGRACAO-LOTES",
                observacao=observacao, usuario_id=None,
            )


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0005_produto_estoque_nao_negativo"),
        ("inventory", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Lote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo", models.CharField(max_length=80)),
                ("quantidade_inicial", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0.01)])),
                ("quantidade_disponivel", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ("data_entrada", models.DateField(default=timezone.localdate)),
                ("data_validade", models.DateField(blank=True, null=True, help_text="Obrigatória em novas entradas; nula somente para saldo legado.")),
                ("custo_unitario", models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ("observacao", models.TextField(blank=True)),
                ("legado", models.BooleanField(default=False, editable=False)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("produto", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="lotes", to="catalog.produto")),
            ],
            options={"ordering": ["data_validade", "data_entrada", "id"]},
        ),
        migrations.AddField(
            model_name="movimentacaoestoque",
            name="lote",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="movimentacoes", to="inventory.lote"),
        ),
        migrations.AddConstraint(model_name="lote", constraint=models.UniqueConstraint(fields=("produto", "codigo"), name="lote_codigo_unico_produto")),
        migrations.AddConstraint(model_name="lote", constraint=models.CheckConstraint(condition=Q(("quantidade_inicial__gt", 0)), name="lote_qtd_inicial_positiva")),
        migrations.AddConstraint(model_name="lote", constraint=models.CheckConstraint(condition=Q(("quantidade_disponivel__gte", 0)), name="lote_qtd_disponivel_nao_negativa")),
        migrations.AddConstraint(model_name="lote", constraint=models.CheckConstraint(condition=Q(("quantidade_disponivel__lte", models.F("quantidade_inicial"))), name="lote_saldo_ate_inicial")),
        migrations.AddConstraint(model_name="lote", constraint=models.CheckConstraint(condition=Q(("custo_unitario__gte", 0)), name="lote_custo_nao_negativo")),
        migrations.AddConstraint(model_name="lote", constraint=models.CheckConstraint(condition=Q(("data_validade__isnull", True)) | Q(("data_validade__gte", models.F("data_entrada"))), name="lote_validade_apos_entrada")),
        migrations.RunPython(migrar_saldos_legados, migrations.RunPython.noop),
    ]
