from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.catalog.models import Produto, Kit
from apps.inventory.models import MovimentacaoEstoque
from .models import Pedido, ItemPedido, Pagamento
@transaction.atomic
def concluir_pedido(pedido, linhas, forma_pagamento, desconto, usuario):
    if pedido.status!="aberto": raise ValidationError("Somente pedidos abertos podem ser concluídos.")
    if not linhas: raise ValidationError("Adicione pelo menos um item à venda.")
    desconto=Decimal(desconto)
    if desconto<0: raise ValidationError("Desconto inválido.")
    total=Decimal("0")
    for linha in linhas:
        qtd=Decimal(linha["quantidade"])
        if qtd<=0: raise ValidationError("Quantidade deve ser maior que zero.")
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
    pedido.forma_pagamento=forma_pagamento; pedido.status="concluido"; pedido.concluido_em=timezone.now(); pedido.save()
    Pagamento.objects.create(pedido=pedido,forma=forma_pagamento,valor=pedido.total)
    for item in pedido.itens.select_related("produto","kit"):
        if item.produto_id:
            p=Produto.objects.select_for_update().get(pk=item.produto_id)
            antes=p.estoque; p.estoque-=item.quantidade; p.save(update_fields=["estoque","atualizado_em"])
            MovimentacaoEstoque.objects.create(produto=p,tipo="venda",quantidade=item.quantidade,saldo_anterior=antes,saldo_posterior=p.estoque,referencia=str(pedido.numero),usuario=usuario)
        elif item.kit_id:
            for comp in item.kit.componentes.select_related("produto"):
                p=Produto.objects.select_for_update().get(pk=comp.produto_id)
                qtd=comp.quantidade*item.quantidade; antes=p.estoque; p.estoque-=qtd; p.save(update_fields=["estoque","atualizado_em"])
                MovimentacaoEstoque.objects.create(produto=p,tipo="venda",quantidade=qtd,saldo_anterior=antes,saldo_posterior=p.estoque,referencia=str(pedido.numero),usuario=usuario,observacao=f"Componente do kit {item.kit.nome}")
    return pedido
@transaction.atomic
def cancelar_pedido(pedido,usuario,justificativa):
    if pedido.status!="concluido": raise ValidationError("Apenas vendas concluídas podem ser canceladas.")
    for item in pedido.itens.select_related("produto","kit"):
        componentes=[]
        if item.produto_id: componentes=[(item.produto,item.quantidade)]
        elif item.kit_id: componentes=[(c.produto,c.quantidade*item.quantidade) for c in item.kit.componentes.select_related("produto")]
        for prod,qtd in componentes:
            p=Produto.objects.select_for_update().get(pk=prod.pk); antes=p.estoque; p.estoque+=qtd; p.save(update_fields=["estoque","atualizado_em"])
            MovimentacaoEstoque.objects.create(produto=p,tipo="estorno",quantidade=qtd,saldo_anterior=antes,saldo_posterior=p.estoque,referencia=str(pedido.numero),usuario=usuario,observacao=justificativa)
    pedido.status="cancelado"; pedido.cancelado_em=timezone.now(); pedido.observacoes=(pedido.observacoes+"\nCancelamento: "+justificativa).strip(); pedido.save()
