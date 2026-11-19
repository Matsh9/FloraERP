from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_alter_produto_estoque_alter_produto_estoque_minimo"),
    ]

    operations = [
        migrations.AddField(
            model_name="produto",
            name="data_validade",
            field=models.DateField(blank=True, null=True),
        ),
    ]
