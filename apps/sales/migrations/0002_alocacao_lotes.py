from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inventory", "0002_lotes_controle"),
        ("sales", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="AlocacaoLote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade", models.DecimalField(decimal_places=2, max_digits=10)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="alocacoes_lote", to="sales.itempedido")),
                ("lote", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="alocacoes_venda", to="inventory.lote")),
            ],
            options={"ordering": ["criado_em", "pk"]},
        ),
        migrations.AddConstraint(
            model_name="alocacaolote",
            constraint=models.CheckConstraint(condition=models.Q(("quantidade__gt", 0)), name="alocacao_lote_qtd_positiva"),
        ),
    ]
