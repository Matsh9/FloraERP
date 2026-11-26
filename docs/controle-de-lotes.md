# Controle de estoque por lotes e validade

## Regras implementadas

- Um lote pertence a um produto e seu código é único dentro desse produto.
- Novas entradas exigem quantidade positiva, data de entrada, validade e custo unitário não negativo.
- O saldo disponível nunca pode ser negativo nem superar a quantidade inicial.
- Entradas atualizam o lote, `Produto.estoque`, `MovimentacaoEstoque` e `RegistroAuditoria` na mesma transação.
- Baixas de venda consomem primeiro os lotes válidos com validade mais próxima (FEFO); lotes sem validade, criados pela migração de saldo legado, ficam por último.
- Lotes vencidos não são elegíveis para venda. O serviço de perdas pode baixar lotes vencidos.
- Cada baixa de venda cria alocações em `AlocacaoLote`, relacionadas ao item da venda e ao lote consumido.
- Cancelamentos devolvem exatamente as quantidades às origens registradas. Vendas antigas sem alocações são bloqueadas para evitar devolução sem rastreabilidade.
- O estoque geral é alterado somente pelos serviços de entrada, baixa e devolução, que conferem a soma dos saldos dos lotes.
- Lotes, alocações e movimentações são preservados; o Django Admin não permite editar/excluir esses registros históricos.

## Endpoints

- `GET /estoque/lotes/`: listagem com filtros por produto, situação e validade.
- `GET/POST /estoque/lotes/entrada/`: entrada de lote (administrador).
- `GET /estoque/alertas/`: estoque mínimo e alertas de validade.
- `GET /estoque/movimentacoes/`: histórico por produto e lote.
- `GET/POST /estoque/perdas/nova/`: registro de perdas por FEFO, incluindo lotes vencidos.

## Migrações

1. `catalog.0004_alter_produto_estoque_decimal`: permite quantidades com até duas casas decimais.
2. `catalog.0005_produto_estoque_nao_negativo`: impede estoque geral negativo.
3. `inventory.0002_lotes_controle`: cria lotes, liga movimentações aos lotes e converte saldos existentes em lotes `LEGADO-*`.
4. `sales.0002_alocacao_lotes`: registra a origem de cada quantidade baixada em vendas.

Execute:

```powershell
python manage.py migrate
python manage.py check
python manage.py test apps.inventory apps.sales apps.core
```

## Observações de implantação

- Faça backup do banco antes das migrações.
- A migração de saldos existentes preserva a quantidade geral. Como o histórico de validade desses saldos não existe no banco anterior, os lotes legados ficam sem data de validade e com uma observação explícita.
- Se houver produtos com saldo negativo, corrija-os antes da migração. A migração/constraint não aceita saldo negativo.
- A validade é considerada até o próprio dia informado; a partir do dia seguinte, o lote é considerado vencido.
- Para concorrência real em produção, prefira PostgreSQL. SQLite não aplica bloqueios de linha (`select_for_update`) como o PostgreSQL.
