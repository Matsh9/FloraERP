from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Categoria,Produto,FichaBotanica,Kit,ItemKit
from apps.customers.models import Cliente
class Command(BaseCommand):
    help="Cria dados fictícios de demonstração do FloraERP sem duplicar registros."
    def handle(self,*args,**options):
        categorias={}
        for nome in ["Flores","Plantas","Vasos e acessórios","Insumos"]:
            categorias[nome],_=Categoria.objects.get_or_create(slug=slugify(nome),defaults={"nome":nome,"descricao":"Categoria demonstrativa"})
        dados=[
          ("Rosa vermelha","FLR-ROSA-001","Flores","18.90","35","10","Rosa para arranjos; mantenha em água limpa."),
          ("Orquídea Phalaenopsis","PLT-ORQ-001","Plantas","79.90","8","3","Prefere luz indireta e regas moderadas."),
          ("Lírio da paz","PLT-LIR-001","Plantas","42.50","12","4","Adapta-se a ambientes com luz indireta."),
          ("Vaso cerâmico P","VAS-CER-001","Vasos e acessórios","24.90","20","5","Vaso decorativo."),
          ("Girassol","FLR-GIR-001","Flores","12.00","0","5","Flor ornamental; estoque demonstrativo zerado."),
        ]
        produtos={}
        for nome,sku,cat,preco,estoque,minimo,desc in dados:
            p,_=Produto.objects.update_or_create(sku=sku,defaults={"nome":nome,"categoria":categorias[cat],"descricao":desc,"preco_venda":Decimal(preco),"custo_aquisicao":Decimal(preco)*Decimal(".45"),"estoque":Decimal(estoque),"estoque_minimo":Decimal(minimo),"ativo":True})
            produtos[sku]=p
            FichaBotanica.objects.update_or_create(produto=p,defaults={"nome_cientifico":{"Rosa vermelha":"Rosa × hybrida","Orquídea Phalaenopsis":"Phalaenopsis spp.","Lírio da paz":"Spathiphyllum wallisii","Girassol":"Helianthus annuus"}.get(nome,""),"iluminacao":"Luz indireta abundante","rega":"Verifique a umidade do substrato antes de regar.","cuidados_especiais":"Dados demonstrativos; ajuste conforme espécie e fornecedor."})
        Cliente.objects.get_or_create(nome="Cliente Demonstração FloraERP",defaults={"telefone":"(11) 90000-0000","whatsapp":"5511900000000","email":"demo@example.invalid","cidade":"Capivari","estado":"SP","observacoes":"Cadastro fictício para demonstração."})
        kit,_=Kit.objects.get_or_create(nome="Presente Botânico Demo",defaults={"descricao":"Kit fictício para testar o PDV.","preco_venda":Decimal("99.90"),"ativo":True})
        ItemKit.objects.get_or_create(kit=kit,produto=produtos["PLT-ORQ-001"],defaults={"quantidade":Decimal("1")})
        ItemKit.objects.get_or_create(kit=kit,produto=produtos["VAS-CER-001"],defaults={"quantidade":Decimal("1")})
        self.stdout.write(self.style.SUCCESS("Dados demonstrativos criados/atualizados sem duplicação."))
