from decimal import Decimal
from django.test import TestCase,Client as TestClient
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from apps.catalog.forms import ProdutoForm
from apps.catalog.models import Categoria,Produto,Kit,ItemKit
from apps.customers.models import Cliente
from apps.inventory.forms import PerdaForm
from apps.sales.models import Pedido
from apps.sales.services import concluir_pedido,cancelar_pedido
from apps.inventory.models import PerdaEstoque,MovimentacaoEstoque
from apps.deliveries.models import Entrega
from django.utils import timezone
class FloraTests(TestCase):
 def setUp(self):
  self.user=get_user_model().objects.create_user(username="admin",password="StrongPass123!",is_superuser=True,is_staff=True)
  self.cat=Categoria.objects.create(nome="Plantas",slug="plantas")
  self.p=Produto.objects.create(nome="Samambaia",sku="SAM-1",categoria=self.cat,preco_venda=Decimal("20.00"),custo_aquisicao=Decimal("8.00"),estoque=Decimal("10"),estoque_minimo=Decimal("2"))
  self.c=Cliente.objects.create(nome="Cliente Teste",telefone="11999999999")
  self.client=TestClient(); self.client.force_login(self.user)
 def test_dashboard_requires_login_and_loads(self):
  c=TestClient(); self.assertRedirects(c.get(reverse("dashboard")),reverse("login")+"?next=/")
  self.assertEqual(self.client.get(reverse("dashboard")).status_code,200)
 def test_product_list(self): self.assertContains(self.client.get(reverse("catalogo_lista")),"Samambaia")
 def test_sale_deducts_stock_and_records_price(self):
  order=Pedido.objects.create(atendente=self.user,cliente=self.c)
  concluir_pedido(order,[{"produto_id":self.p.pk,"quantidade":"2"}],"pix",Decimal("5"),self.user)
  self.p.refresh_from_db(); order.refresh_from_db()
  self.assertEqual(self.p.estoque,Decimal("8")); self.assertEqual(order.total,Decimal("35.00"))
  self.assertEqual(order.itens.first().preco_unitario,Decimal("20.00"))
 def test_sale_blocks_negative_stock(self):
  order=Pedido.objects.create(atendente=self.user)
  with self.assertRaises(ValidationError): concluir_pedido(order,[{"produto_id":self.p.pk,"quantidade":"20"}],"pix",Decimal("0"),self.user)
  self.p.refresh_from_db(); self.assertEqual(self.p.estoque,Decimal("10"))
 def test_kit_deducts_components(self):
  kit=Kit.objects.create(nome="Kit",preco_venda=Decimal("30"))
  ItemKit.objects.create(kit=kit,produto=self.p,quantidade=Decimal("2"))
  order=Pedido.objects.create(atendente=self.user)
  concluir_pedido(order,[{"kit_id":kit.pk,"quantidade":"2"}],"pix",Decimal("0"),self.user)
  self.p.refresh_from_db(); self.assertEqual(self.p.estoque,Decimal("6"))
 def test_cancel_restores_stock_without_deleting_history(self):
  order=Pedido.objects.create(atendente=self.user)
  concluir_pedido(order,[{"produto_id":self.p.pk,"quantidade":"1"}],"pix",Decimal("0"),self.user)
  cancelar_pedido(order,self.user,"Teste de estorno")
  self.p.refresh_from_db(); order.refresh_from_db()
  self.assertEqual(self.p.estoque,Decimal("10")); self.assertEqual(order.status,"cancelado")
  self.assertTrue(MovimentacaoEstoque.objects.filter(tipo="estorno").exists())
 def test_low_stock_alert(self):
  self.p.estoque=Decimal("2"); self.p.save()
  self.assertEqual(self.client.get(reverse("estoque_alertas")).status_code,200)
 def test_producto_form_restricts_integer_stock_and_labels_currency_and_sku(self):
  form = ProdutoForm(data={
   "nome": "Rosa",
   "sku": "ROS-001",
   "categoria": self.cat.pk,
   "descricao": "Teste",
   "preco_venda": "29.90",
   "custo_aquisicao": "12.50",
   "estoque": "3.5",
   "estoque_minimo": "1",
   "unidade": "un",
   "ativo": True,
  })
  self.assertFalse(form.is_valid())
  self.assertIn("Estoque", form.fields["estoque"].label)
  self.assertIn("R$", form.fields["preco_venda"].label)
  self.assertIn("SKU", form.fields["sku"].label)
  self.assertIn("\"", form.fields["sku"].label)
  self.assertIn("Código", form.fields["sku"].label)

 def test_loss_form_calculates_cost_from_product_times_quantity(self):
  self.p.preco_venda = Decimal("42.50")
  self.p.save(update_fields=["preco_venda"])
  form = PerdaForm(data={
   "produto": self.p.pk,
   "quantidade": "2",
   "motivo": "murcho",
   "observacao": "Teste",
   "custo_estimado": "",
  })
  self.assertTrue(form.is_valid(), form.errors)
  self.assertEqual(form.cleaned_data["custo_estimado"], Decimal("85.00"))

 def test_cpf_validation(self):
  c=Cliente(nome="CPF",telefone="11999",cpf="111.111.111-11")
  with self.assertRaises(ValidationError): c.full_clean()
