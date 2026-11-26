import json
import uuid
from datetime import timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import PerdaEstoque, MovimentacaoEstoque, Lote
from .forms import PerdaForm, EntradaLoteForm
from .services import registrar_entrada, baixar_estoque
from apps.catalog.models import Produto
from apps.core.models import RegistroAuditoria


def admin_required(view):
    return user_passes_test(lambda u:u.is_superuser or u.groups.filter(name="Administrador").exists())(view)


@login_required
def lotes(request):
    qs=Lote.objects.select_related("produto").all()
    produto=request.GET.get("produto","")
    situacao=request.GET.get("situacao","")
    validade=request.GET.get("validade","")
    hoje=timezone.localdate()
    if produto.isdigit(): qs=qs.filter(produto_id=int(produto))
    if situacao=="sem_saldo": qs=qs.filter(quantidade_disponivel__lte=0)
    elif situacao=="vencido": qs=qs.filter(quantidade_disponivel__gt=0,data_validade__lt=hoje)
    elif situacao=="proximo_vencimento": qs=qs.filter(quantidade_disponivel__gt=0,data_validade__gte=hoje,data_validade__lte=hoje+timedelta(days=30))
    elif situacao=="com_saldo": qs=qs.filter(quantidade_disponivel__gt=0).filter(Q(data_validade__isnull=True)|Q(data_validade__gt=hoje+timedelta(days=30)))
    if validade=="vencidos": qs=qs.filter(data_validade__lt=hoje,quantidade_disponivel__gt=0)
    elif validade=="30_dias": qs=qs.filter(data_validade__gte=hoje,data_validade__lte=hoje+timedelta(days=30),quantidade_disponivel__gt=0)
    elif validade=="sem_validade": qs=qs.filter(data_validade__isnull=True)
    return render(request,"inventory/lotes.html",{"lotes":qs,"produtos":Produto.objects.filter(ativo=True).order_by("nome"),"produto_filtro":produto,"situacao_filtro":situacao,"validade_filtro":validade,"hoje":hoje})


@login_required
@admin_required
@transaction.atomic
def entrada_lote(request):
    form=EntradaLoteForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        d=form.cleaned_data
        try:
            lote=registrar_entrada(d["produto"],d["codigo"],d["quantidade_inicial"],d["data_entrada"],d["data_validade"],d["custo_unitario"],request.user,d["observacao"])
            RegistroAuditoria.objects.create(usuario=request.user,acao="entrada_lote",entidade="Lote",entidade_id=lote.pk,detalhes=f"{lote.produto.sku}; lote {lote.codigo}; quantidade {lote.quantidade_inicial}")
            messages.success(request,"Entrada registrada e estoque atualizado.")
            return redirect("estoque_lotes")
        except (ValidationError,ValueError,IntegrityError) as exc:
            form.add_error(None,exc.message if hasattr(exc,"message") else "Não foi possível registrar a entrada. Verifique se o código do lote já existe.")
    return render(request,"shared/form.html",{"form":form,"titulo":"Entrada de lote"})


@login_required
def alertas(request):
    hoje=timezone.localdate(); limite=hoje+timedelta(days=30)
    baixo=Produto.objects.filter(ativo=True,estoque__lte=F("estoque_minimo"))
    lotes_alerta=Lote.objects.filter(quantidade_disponivel__gt=0,data_validade__isnull=False,data_validade__lte=limite)
    produtos_ids=lotes_alerta.values_list("produto_id",flat=True)
    produtos=Produto.objects.filter(ativo=True).filter(Q(estoque__lte=F("estoque_minimo"))|Q(pk__in=produtos_ids)).select_related("categoria").distinct()
    return render(request,"inventory/alertas.html",{"produtos":produtos,"baixo":baixo.count(),"validade":lotes_alerta.count(),"hoje":hoje,"lotes_alerta":lotes_alerta.select_related("produto"),"produtos_validade_ids":list(produtos_ids)})


@login_required
def movimentacoes(request):
    return render(request,"inventory/movimentacoes.html",{"movimentacoes":MovimentacaoEstoque.objects.select_related("produto","lote","usuario")[:300]})


@login_required
@admin_required
@transaction.atomic
def registrar_perda(request):
    form=PerdaForm(request.POST or None)
    if request.method=="POST" and form.is_valid():
        try:
            perda=form.save(commit=False)
            referencia_perda=f"PERDA-{uuid.uuid4()}"
            alocacoes=baixar_estoque(perda.produto,perda.quantidade,tipo="perda",usuario=request.user,referencia=referencia_perda,observacao=f"{perda.get_motivo_display()}: {perda.observacao}")
            perda.custo_estimado=sum((l.custo_unitario*q for l,q in alocacoes),Decimal("0"))
            perda.usuario=request.user
            perda.save()
            movimento=MovimentacaoEstoque.objects.filter(referencia=referencia_perda).order_by("-pk").first()
            perda.movimentacao=movimento; perda.save(update_fields=["movimentacao"])
            RegistroAuditoria.objects.create(usuario=request.user,acao="perda_estoque",entidade="PerdaEstoque",entidade_id=perda.pk,detalhes=f"Produto {perda.produto.sku}; quantidade {perda.quantidade}; custo {perda.custo_estimado}")
            messages.success(request,"Perda registrada e lotes atualizados."); return redirect("estoque_movimentacoes")
        except (ValidationError,ValueError) as exc:
            form.add_error(None,exc.message if hasattr(exc,"message") else str(exc))
    produtos=Produto.objects.filter(ativo=True).order_by("nome").values("id","preco_venda","custo_aquisicao")
    produtos_json={str(x["id"]):str(x["custo_aquisicao"] or 0) for x in produtos}
    return render(request,"shared/form.html",{"form":form,"titulo":"Registrar perda de estoque","produtos_json":json.dumps(produtos_json)})
