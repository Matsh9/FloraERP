from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog", "0004_alter_produto_estoque_decimal")]
    operations = [
        migrations.AddConstraint(
            model_name="produto",
            constraint=models.CheckConstraint(condition=models.Q(("estoque__gte", 0)), name="produto_estoque_nao_negativo"),
        ),
        migrations.AddConstraint(
            model_name="produto",
            constraint=models.CheckConstraint(condition=models.Q(("estoque_minimo__gte", 0)), name="produto_estoque_minimo_nao_negativo"),
        ),
    ]
