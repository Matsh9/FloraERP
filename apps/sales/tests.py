from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.catalog.models import Categoria, Produto
from .models import Pedido, Pagamento
from apps.inventory.models import Lote
from .services import concluir_pedido


class PagamentoManagementTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="atendente", password="senha123")
        self.categoria = Categoria.objects.create(nome="Flores", slug="flores")
        self.produto = Produto.objects.create(
            nome="Rosa",
            sku="ROS-001",
            categoria=self.categoria,
            preco_venda=Decimal("50.00"),
            estoque=10,
            ativo=True,
        )
        from django.utils import timezone
        Lote.objects.create(produto=self.produto, codigo="TESTE-001", quantidade_inicial=10,
            quantidade_disponivel=10, data_entrada=timezone.localdate(), custo_unitario=8, legado=True)

    def test_pedido_calcula_totais_baseados_nos_pagamentos(self):
        pedido = Pedido.objects.create(total=Decimal("80.00"))
        Pagamento.objects.create(pedido=pedido, forma="pix", valor=Decimal("50.00"))
        Pagamento.objects.create(pedido=pedido, forma="dinheiro", valor=Decimal("30.00"))

        self.assertEqual(pedido.total_pago, Decimal("80.00"))
        self.assertEqual(pedido.valor_restante, Decimal("0.00"))
        self.assertTrue(pedido.esta_pago)

    def test_concluir_pedido_aceita_pagamentos_mistos(self):
        pedido = Pedido.objects.create(atendente=self.user)

        concluir_pedido(
            pedido,
            [{"produto_id": self.produto.pk, "quantidade": Decimal("2")}],
            "misto",
            Decimal("0"),
            self.user,
            pagamentos=[
                {"forma": "pix", "valor": Decimal("40.00")},
                {"forma": "dinheiro", "valor": Decimal("60.00")},
            ],
        )

        self.assertEqual(pedido.forma_pagamento, "misto")
        self.assertEqual(pedido.total_pago, Decimal("100.00"))
        self.assertEqual(pedido.pagamentos.count(), 2)
