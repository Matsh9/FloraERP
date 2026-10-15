from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F, DecimalField, ExpressionWrapper
from django.shortcuts import render
from django.utils import timezone
from apps.catalog.models import Produto
from apps.sales.models import Pedido, ItemPedido
from apps.deliveries.models import Entrega
from apps.inventory.models import PerdaEstoque
@login_required
def dashboard(request):
    hoje=timezone.localdate()
    vendas=Pedido.objects.filter(status="concluido",concluido_em__date=hoje)
    faturamento=vendas.aggregate(v=Sum("total"))["v"] or Decimal("0")
    total_vendas=vendas.count()
    top=ItemPedido.objects.filter(pedido__status="concluido").values("nome_item").annotate(qtd=Sum("quantidade")).order_by("-qtd")[:5]
    ultimas=Pedido.objects.select_related("cliente","atendente").all()[:8]
    baixo=Produto.objects.filter(ativo=True,estoque__lte=F("estoque_minimo")).count()
    zero=Produto.objects.filter(ativo=True,estoque=0).count()
    pendentes=Pedido.objects.filter(status="aberto").count()
    entregas=Entrega.objects.filter(data_entrega=hoje).exclude(status__in=["entregue","cancelada"]).count()
    perdas=PerdaEstoque.objects.filter(criado_em__date=hoje).count()
    dias=[hoje-timedelta(days=i) for i in reversed(range(7))]
    vendas_dias=[{"dia":d.strftime("%d/%m"),"total":float(Pedido.objects.filter(status="concluido",concluido_em__date=d).aggregate(v=Sum("total"))["v"] or 0)} for d in dias]
    return render(request,"dashboard/index.html",{"faturamento":faturamento,"total_vendas":total_vendas,
      "ticket":faturamento/total_vendas if total_vendas else Decimal("0"),"produtos":Produto.objects.filter(ativo=True).count(),
      "baixo":baixo,"zero":zero,"pendentes":pendentes,"entregas":entregas,"perdas":perdas,
      "top":top,"ultimas":ultimas,"vendas_dias":vendas_dias})
@login_required
def pesquisa_global(request):
    q=request.GET.get("q","").strip()[:100]
    produtos=Produto.objects.filter(nome__icontains=q)|Produto.objects.filter(sku__icontains=q) if q else Produto.objects.none()
    from apps.customers.models import Cliente
    clientes=Cliente.objects.filter(nome__icontains=q) if q else Cliente.objects.none()
    pedidos=Pedido.objects.filter(numero__icontains=q) if q else Pedido.objects.none()
    return render(request,"core/pesquisa.html",{"q":q,"produtos":produtos.distinct()[:10],"clientes":clientes[:10],"pedidos":pedidos[:10]})
