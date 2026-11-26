from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.catalog.models import Produto, Kit
from apps.inventory.models import MovimentacaoEstoque
from apps.inventory.services import baixar_estoque, devolver_ao_lote
from .models import Pedido, ItemPedido, Pagamento, AlocacaoLote


def _normalizar_pagamentos(forma_pagamento, pagamentos=None):
    if pagamentos is None:
        return [{"forma": forma_pagamento}]
    if isinstance(pagamentos, dict):
        return [pagamentos]
    if isinstance(pagamentos, (list, tuple)):
        return list(pagamentos)
    raise ValidationError("Pagamentos informados em formato inválido.")


@transaction.atomic
def concluir_pedido(pedido, linhas, forma_pagamento, desconto, usuario, pagamentos=None):
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if pedido.status!="aberto": raise ValidationError("Somente pedidos abertos podem ser concluídos.")
    if not linhas: raise ValidationError("Adicione pelo menos um item à venda.")
    # Bloqueia os produtos em ordem determinística para reduzir deadlocks entre vendas simultâneas.
    ids_produtos = set()
    for linha in linhas:
        if linha.get("kit_id"):
            kit_lock = Kit.objects.get(pk=linha["kit_id"], ativo=True)
            ids_produtos.update(kit_lock.componentes.values_list("produto_id", flat=True))
        else:
            ids_produtos.add(int(linha["produto_id"]))
    list(Produto.objects.select_for_update().filter(pk__in=ids_produtos).order_by("pk"))
    desconto=Decimal(desconto)
    if desconto<0: raise ValidationError("Desconto inválido.")
    total=Decimal("0")
    for linha in linhas:
        qtd=Decimal(linha["quantidade"])
        if not qtd.is_finite() or qtd <= 0: raise ValidationError("Quantidade deve ser maior que zero.")
        if qtd.as_tuple().exponent < -2: raise ValidationError("A quantidade deve ter no máximo duas casas decimais.")
        if linha.get("kit_id"):
            kit=Kit.objects.get(pk=linha["kit_id"],ativo=True)
            comps=list(kit.componentes.select_related("produto"))
            if not comps: raise ValidationError(f"O kit {kit.nome} não possui componentes.")
            for comp in comps:
                p=Produto.objects.select_for_update().get(pk=comp.produto_id)
                necessaria=comp.quantidade*qtd
                if p.estoque<necessaria: raise ValidationError(f"Estoque insuficiente para {p.nome}.")
            nome,preco,produto,kit_obj=kit.nome,kit.preco_venda,None,kit
        else:
            p=Produto.objects.select_for_update().get(pk=linha["produto_id"],ativo=True)
            if p.estoque<qtd: raise ValidationError(f"Estoque insuficiente para {p.nome}.")
            nome,preco,produto,kit_obj=p.nome,p.preco_venda,p,None
        item_total=preco*qtd; total+=item_total
        ItemPedido.objects.create(pedido=pedido,produto=produto,kit=kit_obj,nome_item=nome,quantidade=qtd,preco_unitario=preco,total=item_total)
    if desconto>total: raise ValidationError("O desconto não pode superar o subtotal.")
    pedido.subtotal=total; pedido.desconto=desconto; pedido.total=total-desconto
    pagamentos = _normalizar_pagamentos(forma_pagamento, pagamentos)
    if not pagamentos: raise ValidationError("Informe ao menos uma forma de pagamento.")

    valor_recebido=Decimal("0")
    lista_pagamentos=[]
    for item in pagamentos:
        metodo = item.get("forma") or forma_pagamento
        valor = Decimal(str(item.get("valor", pedido.total)))
        if metodo not in dict(Pedido.PAGAMENTOS):
            raise ValidationError("Forma de pagamento inválida.")
        if valor<=0: raise ValidationError("Valor do pagamento deve ser maior que zero.")
        valor_recebido += valor
        lista_pagamentos.append({"forma": metodo, "valor": valor, "referencia": item.get("referencia","")})

    if abs(valor_recebido - pedido.total) > Decimal("0.01"):
        raise ValidationError("A soma dos pagamentos deve corresponder ao total da venda.")

    pedido.forma_pagamento = "misto" if len(lista_pagamentos) > 1 or forma_pagamento == "misto" else forma_pagamento
    pedido.status="concluido"; pedido.concluido_em=timezone.now(); pedido.save()

    for item in lista_pagamentos:
        Pagamento.objects.create(pedido=pedido, forma=item["forma"], valor=item["valor"], referencia=item["referencia"])

    for item in pedido.itens.select_related("produto","kit"):
        componentes = [(item.produto, item.quantidade, "")] if item.produto_id else [
            (c.produto, c.quantidade * item.quantidade, f"Componente do kit {item.kit.nome}")
            for c in item.kit.componentes.select_related("produto")
        ]
        for produto, qtd, detalhe in componentes:
            alocacoes = baixar_estoque(produto, qtd, tipo="venda", usuario=usuario,
                referencia=str(pedido.numero), observacao=detalhe or f"Venda {pedido.numero}")
            for lote, quantidade_alocada in alocacoes:
                AlocacaoLote.objects.create(item=item, lote=lote, quantidade=quantidade_alocada)
    return pedido


@transaction.atomic
def registrar_pagamento(pedido, forma_pagamento, valor, referencia="", usuario=None):
    if not forma_pagamento:
        raise ValidationError("Selecione uma forma de pagamento.")
    return pedido.registrar_pagamento(forma_pagamento, valor, referencia)


@transaction.atomic
def cancelar_pedido(pedido, usuario, justificativa):
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if pedido.status != "concluido":
        raise ValidationError("Apenas vendas concluídas podem ser canceladas.")
    itens = list(pedido.itens.select_related("produto", "kit").prefetch_related("alocacoes_lote__lote"))
    if any(not item.alocacoes_lote.exists() for item in itens):
        raise ValidationError("Esta venda não possui rastreabilidade dos lotes (venda anterior à implantação). Não é possível devolver automaticamente; faça um ajuste de estoque auditado.")
    ids_produtos = {a.lote.produto_id for item in itens for a in item.alocacoes_lote.select_related("lote")}
    list(Produto.objects.select_for_update().filter(pk__in=ids_produtos).order_by("pk"))
    for item in itens:
        for alocacao in item.alocacoes_lote.select_related("lote", "lote__produto"):
            devolver_ao_lote(alocacao.lote.produto, alocacao.lote, alocacao.quantidade,
                usuario=usuario, referencia=str(pedido.numero),
                observacao=f"Cancelamento da venda {pedido.numero}: {justificativa}")
    pedido.status = "cancelado"
    pedido.cancelado_em = timezone.now()
    pedido.observacoes = (pedido.observacoes + chr(10) + "Cancelamento: " + justificativa).strip()
    pedido.save(update_fields=["status", "cancelado_em", "observacoes"])
    return pedido


@transaction.atomic
def criar_pedido_personalizado(pedido, linhas, usuario):
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if pedido.status != "aberto":
        raise ValidationError("Somente pedidos abertos podem receber itens.")
    if not linhas:
        raise ValidationError("Adicione pelo menos um produto ao pedido.")

    pedido.atendente = usuario
    ids_produtos = set()
    for linha in linhas:
        if linha.get("kit_id"):
            kit = Kit.objects.select_for_update().get(pk=linha["kit_id"], ativo=True)
            ids_produtos.update(kit.componentes.values_list("produto_id", flat=True))
        else:
            ids_produtos.add(int(linha["produto_id"]))
    list(Produto.objects.select_for_update().filter(pk__in=ids_produtos).order_by("pk"))

    subtotal = Decimal("0")
    for linha in linhas:
        quantidade = Decimal(str(linha["quantidade"]))
        if not quantidade.is_finite() or quantidade <= 0:
            raise ValidationError("Quantidade deve ser maior que zero.")
        if quantidade.as_tuple().exponent < -2:
            raise ValidationError("A quantidade deve ter no máximo duas casas decimais.")

        if linha.get("kit_id"):
            kit = Kit.objects.get(pk=linha["kit_id"], ativo=True)
            nome = kit.nome
            preco = kit.preco_venda
            produto = None
        else:
            produto = Produto.objects.get(pk=linha["produto_id"], ativo=True)
            nome = produto.nome
            preco = produto.preco_venda
            kit = None

        item_total = preco * quantidade
        subtotal += item_total
        ItemPedido.objects.create(
            pedido=pedido,
            produto=produto,
            kit=kit,
            nome_item=nome,
            quantidade=quantidade,
            preco_unitario=preco,
            total=item_total,
        )

    pedido.subtotal = subtotal
    pedido.desconto = Decimal("0")
    pedido.total = subtotal
    pedido.save(update_fields=["atendente", "subtotal", "desconto", "total"])
    return pedido
