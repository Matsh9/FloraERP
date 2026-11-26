from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [("catalog", "0003_produto_data_validade")]
    operations = [
        migrations.AlterField(model_name="produto", name="estoque", field=models.DecimalField(max_digits=10, decimal_places=2, default=0)),
        migrations.AlterField(model_name="produto", name="estoque_minimo", field=models.DecimalField(max_digits=10, decimal_places=2, default=0)),
    ]
