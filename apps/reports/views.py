import csv
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from apps.sales.models import Pedido, ItemPedido
from apps.inventory.models import PerdaEstoque, Lote
from apps.catalog.models import Produto


def admin_required(view):
    return user_passes_test(lambda u: u.is_superuser or u.groups.filter(name="Administrador").exists())(view)


@login_required
@admin_required
def index(request):
    hoje = timezone.localdate()
    inicio = request.GET.get("inicio") or (hoje - timedelta(days=30)).isoformat()
    fim = request.GET.get("fim") or hoje.isoformat()
    vendas = Pedido.objects.filter(status="concluido", concluido_em__date__gte=inicio, concluido_em__date__lte=fim)
    total = vendas.aggregate(s=Sum("total"))["s"] or Decimal("0")
    itens = ItemPedido.objects.filter(pedido__in=vendas).values("nome_item").annotate(
        qtd=Sum("quantidade"), valor=Sum("total")
    ).order_by("-qtd")[:20]
    perdas = PerdaEstoque.objects.filter(criado_em__date__gte=inicio, criado_em__date__lte=fim).select_related("produto")
    produtos_estoque = Produto.objects.filter(ativo=True).annotate(
        saldo_lotes=Sum("lotes__quantidade_disponivel"),
        quantidade_lotes=Count("lotes", distinct=True),
    ).order_by("nome")
    lotes_vencimento = Lote.objects.filter(
        quantidade_disponivel__gt=0,
        data_validade__isnull=False,
        data_validade__lte=hoje + timedelta(days=30),
    ).select_related("produto").order_by("data_validade")
    return render(request, "reports/index.html", {
        "inicio": inicio, "fim": fim, "vendas": vendas, "total": total,
        "itens": itens, "perdas": perdas, "produtos": produtos_estoque,
        "lotes_vencimento": lotes_vencimento,
    })


@login_required
@admin_required
def exportar_vendas(request):
    inicio = request.GET.get("inicio")
    fim = request.GET.get("fim")
    qs = Pedido.objects.filter(status="concluido").select_related("cliente", "atendente")
    if inicio:
        qs = qs.filter(concluido_em__date__gte=inicio)
    if fim:
        qs = qs.filter(concluido_em__date__lte=fim)
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="floraerp-vendas.csv"'
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["Pedido", "Data", "Cliente", "Atendente", "Subtotal", "Desconto", "Total", "Pagamento"])
    for pedido in qs:
        writer.writerow([
            pedido.numero, pedido.concluido_em, pedido.cliente.nome if pedido.cliente else "",
            pedido.atendente.get_username() if pedido.atendente else "", pedido.subtotal,
            pedido.desconto, pedido.total, pedido.get_forma_pagamento_display(),
        ])
    return response
