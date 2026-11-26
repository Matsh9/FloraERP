from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.suppliers.models import Fornecedor


class FornecedorTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin-fornecedor", email="admin@example.com", password="senha123"
        )

    def test_criar_fornecedor_por_formulario(self):
        client = self.client
        client.force_login(self.user)
        response = client.post("/fornecedores/novo/", {
            "razao_social": "Flores Brasil Distribuidora LTDA",
            "nome_fantasia": "Flores Brasil",
            "cnpj": "11.222.333/0001-81",
            "telefone": "(11) 99999-0000",
            "ativo": "on",
        })
        fornecedor = Fornecedor.objects.get(nome_fantasia="Flores Brasil")
        self.assertRedirects(response, f"/fornecedores/{fornecedor.pk}/")

    def test_cnpj_ficcional_e_aceito(self):
        client = self.client
        client.force_login(self.user)
        response = client.post("/fornecedores/novo/", {
            "razao_social": "Fornecedor Fictício",
            "cnpj": "300 303 030 999 99",
            "ativo": "on",
        })
        fornecedor = Fornecedor.objects.get(razao_social="Fornecedor Fictício")
        self.assertRedirects(response, f"/fornecedores/{fornecedor.pk}/")

    def test_consulta_e_edicao_na_mesma_pagina(self):
        fornecedor = Fornecedor.objects.create(
            razao_social="Fornecedor de Mudas", cnpj="11222333000181", ativo=True
        )
        client = self.client
        self.assertEqual(client.get("/fornecedores/").status_code, 302)
        client.force_login(self.user)

        response = client.get("/fornecedores/", {"q": "Mudas"})
        self.assertContains(response, "Fornecedor de Mudas")

        response = client.get(f"/fornecedores/{fornecedor.pk}/?editar=1")
        self.assertContains(response, "Salvar alterações")

        response = client.post(f"/fornecedores/{fornecedor.pk}/", {
            "razao_social": "Fornecedor Atualizado",
            "nome_fantasia": "Mudas Top",
            "cnpj": "11222333000181",
            "ativo": "on",
        })
        self.assertRedirects(response, f"/fornecedores/{fornecedor.pk}/")
        fornecedor.refresh_from_db()
        self.assertEqual(fornecedor.razao_social, "Fornecedor Atualizado")
