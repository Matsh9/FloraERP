from django.db import models
class Categoria(models.Model):
    nome=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(unique=True)
    descricao=models.TextField(blank=True)
    ativa=models.BooleanField(default=True)
    def __str__(self): return self.nome
class Produto(models.Model):
    UNIDADES=[("un","Unidade"),("vaso","Vaso"),("muda","Muda"),("pct","Pacote"),("kg","Kg"),("m","Metro")]
    nome=models.CharField(max_length=160)
    sku=models.CharField(max_length=40,unique=True)
    categoria=models.ForeignKey(Categoria,on_delete=models.PROTECT,related_name="produtos")
    descricao=models.TextField(blank=True)
    imagem=models.ImageField(upload_to="produtos/",blank=True,null=True)
    preco_venda=models.DecimalField(max_digits=10,decimal_places=2)
    custo_aquisicao=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    estoque=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    estoque_minimo=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    unidade=models.CharField(max_length=10,choices=UNIDADES,default="un")
    ativo=models.BooleanField(default=True)
    criado_em=models.DateTimeField(auto_now_add=True)
    atualizado_em=models.DateTimeField(auto_now=True)
    class Meta: ordering=["nome"]
    def __str__(self): return f"{self.nome} ({self.sku})"
    @property
    def estoque_baixo(self): return self.estoque <= self.estoque_minimo
class FichaBotanica(models.Model):
    produto=models.OneToOneField(Produto,on_delete=models.CASCADE,related_name="ficha_botanica")
    nome_cientifico=models.CharField(max_length=180,blank=True)
    iluminacao=models.CharField(max_length=180,blank=True)
    rega=models.TextField(blank=True)
    temperatura=models.CharField(max_length=180,blank=True)
    cuidados_especiais=models.TextField(blank=True)
    beneficios_usos=models.TextField(blank=True,help_text="Informação educativa; não substitui orientação profissional.")
    argumentos_venda=models.TextField(blank=True)
    complementares=models.ManyToManyField(Produto,blank=True,related_name="recomendado_com")
    def __str__(self): return f"Ficha: {self.produto.nome}"
class Kit(models.Model):
    nome=models.CharField(max_length=140)
    descricao=models.TextField(blank=True)
    imagem=models.ImageField(upload_to="kits/",blank=True,null=True)
    preco_venda=models.DecimalField(max_digits=10,decimal_places=2)
    ativo=models.BooleanField(default=True)
    criado_em=models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.nome
class ItemKit(models.Model):
    kit=models.ForeignKey(Kit,on_delete=models.CASCADE,related_name="componentes")
    produto=models.ForeignKey(Produto,on_delete=models.PROTECT)
    quantidade=models.DecimalField(max_digits=8,decimal_places=2)
    class Meta: constraints=[models.UniqueConstraint(fields=["kit","produto"],name="kit_produto_unico")]
