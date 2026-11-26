from datetime import timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from apps.catalog.models import Categoria, Produto, Kit, ItemKit
from apps.sales.models import Pedido, AlocacaoLote
from apps.sales.services import concluir_pedido, cancelar_pedido
from .models import Lote, MovimentacaoEstoque
from .services import registrar_entrada, baixar_estoque


class ControleLotesTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="estoquista", password="teste123")
        categoria = Categoria.objects.create(nome="Flores", slug="flores")
        self.produto = Produto.objects.create(nome="Rosa vermelha", sku="ROSA-01", categoria=categoria,
            preco_venda=Decimal("10.00"), custo_aquisicao=Decimal("4.00"), estoque=0)
        self.hoje = timezone.localdate()

    def entrada(self, codigo, qtd, validade_dias, data_entrada=None):
        return registrar_entrada(self.produto, codigo, Decimal(str(qtd)), data_entrada or (self.hoje + timedelta(days=min(validade_dias, 0) - 10)),
            self.hoje + timedelta(days=validade_dias), Decimal("4.00"), self.user, "Entrada de teste")

    def test_entrada_cria_lote_atualiza_saldo_e_movimentacao(self):
        lote = self.entrada("L001", 10, 20)
        self.produto.refresh_from_db()
        self.assertEqual(lote.quantidade_disponivel, Decimal("10"))
        self.assertEqual(self.produto.estoque, Decimal("10"))
        self.assertEqual(MovimentacaoEstoque.objects.filter(lote=lote, tipo="entrada", usuario=self.user).count(), 1)

    def test_codigo_duplicado_no_mesmo_produto_e_bloqueado(self):
        self.entrada("L001", 5, 20)
        with self.assertRaises(ValidationError):
            self.entrada("L001", 2, 30)

    def test_fefo_consumo_em_multiplos_lotes(self):
        l1 = self.entrada("L001", 10, 5)
        l2 = self.entrada("L002", 15, 15)
        alocacoes = baixar_estoque(self.produto, 12, usuario=self.user, tipo="venda")
        l1.refresh_from_db(); l2.refresh_from_db(); self.produto.refresh_from_db()
        self.assertEqual([(x.pk, q) for x, q in alocacoes], [(l1.pk, Decimal("10")), (l2.pk, Decimal("2"))])
        self.assertEqual(l1.quantidade_disponivel, Decimal("0"))
        self.assertEqual(l2.quantidade_disponivel, Decimal("13"))
        self.assertEqual(self.produto.estoque, Decimal("13"))

    def test_bloqueia_lote_vencido_e_estoque_insuficiente(self):
        vencido = self.entrada("VENCIDO", 5, -1)
        self.produto.refresh_from_db()
        with self.assertRaises(ValidationError):
            baixar_estoque(self.produto, 1, usuario=self.user)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, Decimal("5"))
        self.assertEqual(vencido.quantidade_disponivel, Decimal("5"))

    def test_fefo_um_lote(self):
        lote = self.entrada("L001", 5, 10)
        baixas = baixar_estoque(self.produto, 3, usuario=self.user)
        lote.refresh_from_db()
        self.assertEqual(baixas[0][0].pk, lote.pk)
        self.assertEqual(lote.quantidade_disponivel, Decimal("2"))

    def test_cancelamento_devolve_aos_lotes_originais(self):
        l1 = self.entrada("L001", 4, 5)
        l2 = self.entrada("L002", 6, 10)
        pedido = Pedido.objects.create(atendente=self.user)
        concluir_pedido(pedido, [{"produto_id": self.produto.pk, "quantidade": "5"}], "pix", Decimal("0"), self.user)
        self.assertEqual(AlocacaoLote.objects.filter(item__pedido=pedido).count(), 2)
        cancelar_pedido(pedido, self.user, "Teste")
        l1.refresh_from_db(); l2.refresh_from_db(); self.produto.refresh_from_db()
        self.assertEqual(l1.quantidade_disponivel, Decimal("4"))
        self.assertEqual(l2.quantidade_disponivel, Decimal("6"))
        self.assertEqual(self.produto.estoque, Decimal("10"))
        self.assertTrue(MovimentacaoEstoque.objects.filter(tipo="estorno", lote=l1).exists())

    def test_perda_consume_lote_vencido_e_registra_historico(self):
        lote = self.entrada("VENCIDO", 3, -1)
        baixas = baixar_estoque(self.produto, 2, tipo="perda", usuario=self.user, observacao="Perda vencimento")
        lote.refresh_from_db(); self.produto.refresh_from_db()
        self.assertEqual(lote.quantidade_disponivel, Decimal("1"))
        self.assertEqual(self.produto.estoque, Decimal("1"))
        self.assertTrue(MovimentacaoEstoque.objects.filter(tipo="perda", lote=lote, quantidade=2).exists())

    def test_kit_consume_componentes_por_lote(self):
        lote = self.entrada("KIT-001", 8, 10)
        kit = Kit.objects.create(nome="Kit flores", preco_venda=Decimal("20"))
        ItemKit.objects.create(kit=kit, produto=self.produto, quantidade=Decimal("2"))
        pedido = Pedido.objects.create(atendente=self.user)
        concluir_pedido(pedido, [{"kit_id": kit.pk, "quantidade": "2"}], "pix", Decimal("0"), self.user)
        lote.refresh_from_db(); self.produto.refresh_from_db()
        self.assertEqual(lote.quantidade_disponivel, Decimal("4"))
        self.assertEqual(self.produto.estoque, Decimal("4"))

    def test_lista_lotes_requer_login_e_exibe_lote(self):
        from django.test import Client
        self.entrada("L001", 2, 10)
        client = Client()
        self.assertEqual(client.get("/estoque/lotes/").status_code, 302)
        client.force_login(self.user)
        response = client.get("/estoque/lotes/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "L001")

    def test_situacoes_e_filtros_de_validade(self):
        vencido = self.entrada("VENCIDO", 2, -1)
        proximo = self.entrada("PROXIMO", 2, 10)
        futuro = self.entrada("FUTURO", 2, 90)
        self.assertEqual(vencido.situacao, "vencido")
        self.assertEqual(proximo.situacao, "proximo_vencimento")
        self.assertEqual(futuro.situacao, "com_saldo")
        from django.test import Client
        client = Client(); client.force_login(self.user)
        resp = client.get("/estoque/lotes/", {"situacao":"vencido"})
        self.assertContains(resp, "VENCIDO")
        self.assertNotContains(resp, "FUTURO")
        resp = client.get("/estoque/lotes/", {"validade":"30_dias"})
        self.assertContains(resp, "PROXIMO")

    def test_historico_guarda_usuario_lote_e_tipo(self):
        lote = self.entrada("AUDIT-01", 3, 20)
        baixar_estoque(self.produto, 1, tipo="perda", usuario=self.user, referencia="PERDA-1", observacao="Avaria")
        mov = MovimentacaoEstoque.objects.get(tipo="perda", lote=lote)
        self.assertEqual(mov.usuario, self.user)
        self.assertEqual(mov.referencia, "PERDA-1")
        self.assertEqual(mov.observacao, "Avaria")
        self.assertEqual(mov.quantidade, Decimal("1"))

    def test_consistencia_entre_saldo_geral_e_soma_dos_lotes(self):
        self.entrada("L001", 7, 10)
        self.entrada("L002", 3, 20)
        total_lotes = sum(Lote.objects.filter(produto=self.produto).values_list("quantidade_disponivel", flat=True), Decimal("0"))
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.estoque, total_lotes)
