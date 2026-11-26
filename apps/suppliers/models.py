import re

from django.core.exceptions import ValidationError
from django.db import models


class Fornecedor(models.Model):
    razao_social = models.CharField("Razão social", max_length=180)
    nome_fantasia = models.CharField("Nome fantasia", max_length=180, blank=True)
    cnpj = models.CharField("CNPJ", max_length=18, blank=True, db_index=True)
    inscricao_estadual = models.CharField("Inscrição estadual", max_length=30, blank=True)
    contato = models.CharField("Pessoa de contato", max_length=120, blank=True)
    telefone = models.CharField("Telefone", max_length=24, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=24, blank=True)
    email = models.CharField("E-mail", max_length=254, blank=True)
    site = models.CharField("Site", max_length=200, blank=True)
    endereco = models.CharField("Endereço", max_length=180, blank=True)
    numero = models.CharField("Número", max_length=20, blank=True)
    complemento = models.CharField("Complemento", max_length=100, blank=True)
    bairro = models.CharField("Bairro", max_length=100, blank=True)
    cidade = models.CharField("Cidade", max_length=100, blank=True)
    estado = models.CharField("Estado", max_length=2, blank=True)
    cep = models.CharField("CEP", max_length=9, blank=True)
    observacoes = models.TextField("Observações", blank=True)
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["razao_social"]
        verbose_name = "fornecedor"
        verbose_name_plural = "fornecedores"

    def __str__(self):
        return self.nome_fantasia or self.razao_social
