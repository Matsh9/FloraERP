import json
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from apps.catalog.models import Produto,Kit
from .models import Pedido,ItemPedido
from .services import concluir_pedido,cancelar_pedido,registrar_pagamento
@login_required
def pdv(request):
 if request.method=="POST":
  try:
   raw=request.POST.get("linhas","[]"); linhas=json.loads(raw)
   if not isinstance(linhas,list) or len(linhas)>100: raise ValidationError("Carrinho inválido.")
   cliente_id=request.POST.get("cliente") or None
   pedido=Pedido.objects.create(atendente=request.user,cliente_id=cliente_id)
   concluir_pedido(pedido,linhas,request.POST.get("forma_pagamento"),Decimal(request.POST.get("desconto","0")),request.user)
   messages.success(request,f"Venda {str(pedido.numero)[:8]} concluída."); return redirect("venda_detalhe",pk=pedido.pk)
  except (ValueError,InvalidOperation,ValidationError,Produto.DoesNotExist,Kit.DoesNotExist) as e:
   if "pedido" in locals() and pedido.pk and pedido.status=="aberto": pedido.delete()
   messages.error(request,e.message if hasattr(e,"message") else str(e))
 produtos=Produto.objects.filter(
  ativo=True, estoque__gt=0, lotes__quantidade_disponivel__gt=0
 ).filter(Q(lotes__data_validade__isnull=True)|Q(lotes__data_validade__gte=timezone.localdate())).select_related("categoria").distinct()
 from apps.customers.models import Cliente
 return render(request,"sales/pdv.html",{"produtos":produtos,"clientes":Cliente.objects.filter(ativo=True),"kits":Kit.objects.filter(ativo=True).prefetch_related("componentes")})
@login_required
def historico(request):
 qs=Pedido.objects.select_related("cliente","atendente").all()
 status=request.GET.get("status","")
 if status: qs=qs.filter(status=status)
 inicio=request.GET.get("inicio"); fim=request.GET.get("fim")
 if inicio: qs=qs.filter(criado_em__date__gte=inicio)
 if fim: qs=qs.filter(criado_em__date__lte=fim)
 return render(request,"sales/historico.html",{"pedidos":qs,"status":status,"inicio":inicio,"fim":fim})
@login_required
def detalhe(request, pk):
    pedido = get_object_or_404(Pedido.objects.select_related("cliente", "atendente").prefetch_related(
        "itens", "itens__alocacoes_lote__lote", "itens__alocacoes_lote__lote__produto", "pagamentos"
    ), pk=pk)
    pode_cancelar = request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()
    return render(request, "sales/detalhe.html", {"pedido": pedido, "pode_cancelar": pode_cancelar})
@login_required
def comprovante(request,pk): return render(request,"sales/comprovante.html",{"pedido":get_object_or_404(Pedido.objects.prefetch_related("itens","pagamentos"),pk=pk)})
@login_required
def pagamento(request,pk):
 p=get_object_or_404(Pedido.objects.prefetch_related("pagamentos"),pk=pk)
 if request.method=="POST":
  try:
   valor=request.POST.get("valor")
   registrar_pagamento(p, request.POST.get("forma_pagamento"), valor, request.POST.get("referencia",""), request.user)
   messages.success(request,"Pagamento registrado com sucesso.")
  except ValidationError as e:
   messages.error(request,str(e))
 return redirect("venda_detalhe",pk=pk)

@login_required
def cancelar(request,pk):
 p=get_object_or_404(Pedido,pk=pk)
 if request.method=="POST":
  if not (request.user.is_superuser or request.user.groups.filter(name="Administrador").exists()):
   messages.error(request,"Somente administradores podem cancelar vendas."); return redirect("venda_detalhe",pk=pk)
  try: cancelar_pedido(p,request.user,request.POST.get("justificativa","").strip() or "Cancelamento administrativo"); messages.success(request,"Venda cancelada e estornada.")
  except ValidationError as e: messages.error(request,str(e))
 return redirect("venda_detalhe",pk=pk)
