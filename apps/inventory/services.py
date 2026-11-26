from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum, F, Q
from django.utils import timezone
from apps.catalog.models import Produto
from .models import Lote, MovimentacaoEstoque


def _decimal(value):
    try:
        value = Decimal(str(value))
    except Exception:
        raise ValidationError("Quantidade inválida.")
    if not value.is_finite() or value <= 0:
        raise ValidationError("A quantidade deve ser maior que zero.")
    if value.as_tuple().exponent < -2:
        raise ValidationError("A quantidade deve ter no máximo duas casas decimais.")
    return value


@transaction.atomic
def registrar_entrada(produto, codigo, quantidade, data_entrada, data_validade, custo_unitario, usuario=None, observacao=""):
    quantidade = _decimal(quantidade)
    produto = Produto.objects.select_for_update().get(pk=produto.pk)
    if not data_validade:
        raise ValidationError("Informe a data de validade do lote.")
    if data_validade < data_entrada:
        raise ValidationError("A validade não pode ser anterior à entrada.")
    custo_unitario = Decimal(str(custo_unitario))
    if not custo_unitario.is_finite() or custo_unitario < 0 or custo_unitario.as_tuple().exponent < -2:
        raise ValidationError("O custo unitário deve ser válido, não negativo e ter até duas casas decimais.")
    lote = Lote(produto=produto, codigo=codigo.strip(), quantidade_inicial=quantidade,
                quantidade_disponivel=quantidade, data_entrada=data_entrada,
                data_validade=data_validade, custo_unitario=custo_unitario, observacao=observacao)
    lote.full_clean()
    lote.save()
    antes = Decimal(str(produto.estoque))
    produto.estoque = antes + quantidade
    produto.save(update_fields=["estoque", "atualizado_em"])
    MovimentacaoEstoque.objects.create(produto=produto, lote=lote, tipo="entrada", quantidade=quantidade,
        saldo_anterior=antes, saldo_posterior=produto.estoque, referencia=f"Lote {lote.codigo}",
        observacao=observacao, usuario=usuario)
    return lote


@transaction.atomic
def baixar_estoque(produto, quantidade, tipo="venda", usuario=None, referencia="", observacao=""):
    quantidade = _decimal(quantidade)
    produto = Produto.objects.select_for_update().get(pk=produto.pk)
    hoje = timezone.localdate()
    lotes = list(Lote.objects.select_for_update().filter(
        produto=produto, quantidade_disponivel__gt=0
    ).filter(models_q_validos(hoje) if tipo != "perda" else Q()).order_by(F("data_validade").asc(nulls_last=True), "data_entrada", "pk"))
    disponivel = sum((l.quantidade_disponivel for l in lotes), Decimal("0"))
    if disponivel < quantidade:
        raise ValidationError(f"Estoque válido insuficiente para {produto.nome}. Disponível em lotes válidos: {disponivel}.")
    saldo_produto = Decimal(str(produto.estoque))
    saldo_lotes = Lote.objects.filter(produto=produto).aggregate(total=Sum("quantidade_disponivel"))["total"] or Decimal("0")
    if saldo_produto != saldo_lotes:
        raise ValidationError(f"Inconsistência de estoque em {produto.nome}: estoque geral {saldo_produto} e lotes {saldo_lotes}. Regularize antes da operação.")
    restante = quantidade
    alocacoes = []
    for lote in lotes:
        if restante <= 0:
            break
        usar = min(lote.quantidade_disponivel, restante)
        lote.quantidade_disponivel -= usar
        lote.save(update_fields=["quantidade_disponivel", "atualizado_em"])
        anterior_produto = Decimal(str(produto.estoque))
        produto.estoque = anterior_produto - usar
        produto.save(update_fields=["estoque", "atualizado_em"])
        MovimentacaoEstoque.objects.create(produto=produto, lote=lote, tipo=tipo, quantidade=usar,
            saldo_anterior=anterior_produto, saldo_posterior=produto.estoque,
            referencia=referencia, observacao=observacao or f"Baixa do lote {lote.codigo}", usuario=usuario)
        alocacoes.append((lote, usar))
        restante -= usar
    return alocacoes


def models_q_validos(hoje):
    from django.db.models import Q
    return Q(data_validade__isnull=True) | Q(data_validade__gte=hoje)


@transaction.atomic
def devolver_ao_lote(produto, lote, quantidade, usuario=None, referencia="", observacao=""):
    quantidade = _decimal(quantidade)
    produto = Produto.objects.select_for_update().get(pk=produto.pk)
    lote = Lote.objects.select_for_update().get(pk=lote.pk, produto=produto)
    if lote.quantidade_disponivel + quantidade > lote.quantidade_inicial:
        raise ValidationError("A devolução excederia a quantidade original do lote.")
    antes = Decimal(str(produto.estoque))
    lote.quantidade_disponivel += quantidade
    lote.save(update_fields=["quantidade_disponivel", "atualizado_em"])
    produto.estoque = antes + quantidade
    produto.save(update_fields=["estoque", "atualizado_em"])
    MovimentacaoEstoque.objects.create(produto=produto, lote=lote, tipo="estorno", quantidade=quantidade,
        saldo_anterior=antes, saldo_posterior=produto.estoque, referencia=referencia,
        observacao=observacao, usuario=usuario)
