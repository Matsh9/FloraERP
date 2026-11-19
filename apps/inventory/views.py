import json
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.shortcuts import render,redirect
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from django.utils import timezone
from .models import PerdaEstoque,MovimentacaoEstoque
from .forms import PerdaForm
from apps.catalog.models import Produto
from apps.core.models import RegistroAuditoria
def admin_required(view): return user_passes_test(lambda u:u.is_superuser or u.groups.filter(name="Administrador").exists())(view)
@login_required
def alertas(request):
 hoje=timezone.localdate()
 limite_validade=hoje+timedelta(days=30)
 baixo=Produto.objects.filter(ativo=True,estoque__lte=F("estoque_minimo"))
 validade=Produto.objects.filter(ativo=True,data_validade__isnull=False,data_validade__lte=limite_validade)
 produtos=Produto.objects.filter(ativo=True).filter(
  Q(estoque__lte=F("estoque_minimo")) |
  Q(data_validade__isnull=False,data_validade__lte=limite_validade)
 ).select_related("categoria")
 return render(request,"inventory/alertas.html",{
  "produtos":produtos,
  "baixo":baixo.count(),
  "validade":validade.count(),
  "hoje":hoje,
 })
@login_required
def movimentacoes(request):
 return render(request,"inventory/movimentacoes.html",{"movimentacoes":MovimentacaoEstoque.objects.select_related("produto","usuario")[:200]})
@login_required
@admin_required
def registrar_perda(request):
 form=PerdaForm(request.POST or None)
 produtos=Produto.objects.filter(ativo=True).order_by("nome").values("id","preco_venda","custo_aquisicao")
 produtos_json={str(p["id"]): str((p["preco_venda"] or p["custo_aquisicao"] or Decimal("0"))) for p in produtos}
 if request.method=="POST" and form.is_valid():
  try:
   with transaction.atomic():
    perda=form.save(commit=False); produto=Produto.objects.select_for_update().get(pk=perda.produto_id)
    if perda.quantidade<=0: raise ValidationError("A quantidade deve ser maior que zero.")
    if produto.estoque<perda.quantidade: raise ValidationError("Estoque insuficiente para registrar essa perda.")
    custo_unitario = produto.preco_venda or produto.custo_aquisicao or Decimal("0")
    perda.custo_estimado = custo_unitario * Decimal(str(perda.quantidade))
    antes=produto.estoque; produto.estoque-=perda.quantidade; produto.save(update_fields=["estoque","atualizado_em"])
    mov=MovimentacaoEstoque.objects.create(produto=produto,tipo="perda",quantidade=perda.quantidade,saldo_anterior=antes,saldo_posterior=produto.estoque,observacao=perda.observacao,usuario=request.user)
    perda.usuario=request.user; perda.movimentacao=mov; perda.save()
    RegistroAuditoria.objects.create(usuario=request.user,acao="perda_estoque",entidade="PerdaEstoque",entidade_id=perda.pk,detalhes=f"Produto {produto.sku}; quantidade {perda.quantidade}; custo {perda.custo_estimado}")
   messages.success(request,"Perda registrada e estoque atualizado."); return redirect("estoque_movimentacoes")
  except (ValidationError,ValueError) as e: form.add_error(None,e.message if hasattr(e,"message") else str(e))
 return render(request,"shared/form.html",{"form":form,"titulo":"Registrar perda de estoque","produtos_json":json.dumps(produtos_json)})
