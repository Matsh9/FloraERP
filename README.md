# FloraERP

ERP web para floriculturas, desenvolvido com Django, templates server-side, SQLite por padrão e opção PostgreSQL. Interface em português brasileiro, moeda BRL e fuso `America/Sao_Paulo`.

## Requisitos
- Python 3.12 ou superior (o projeto também pode funcionar em versões mais novas compatíveis com Django).
- Windows 10/11 ou sistema com Python.
- Node.js não é necessário.

## Instalação no Windows PowerShell

```powershell
# 1. Entre na pasta do projeto
cd FloraERP

# 2. Verifique a versão do Python
python --version

# 3. Crie e ative o ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Se o PowerShell bloquear a ativação, execute nesta janela:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# 4. Instale as dependências
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 5. Opcional: copie as configurações de exemplo
Copy-Item .env.example .env
# Edite .env e defina DJANGO_SECRET_KEY para um segredo aleatório antes de produção.
# As variáveis de ambiente do arquivo .env não são carregadas automaticamente;
# defina-as na sessão do PowerShell ou instale python-dotenv e carregue-as no ambiente.

# 6. Crie as migrações e aplique-as
python manage.py makemigrations catalog customers inventory sales deliveries core
python manage.py migrate

# 7. Crie seu próprio administrador (não existe senha padrão)
python manage.py createsuperuser

# 8. Opcional: dados fictícios de demonstração
python manage.py seed_demo

# 9. Verifique o projeto e os testes
python manage.py check
python manage.py test

# 10. Inicie o servidor local
python manage.py runserver
```

Abra:
- Aplicação: http://127.0.0.1:8000/
- Administração Django: http://127.0.0.1:8000/admin/
- Login: http://127.0.0.1:8000/accounts/login/

## Perfis e permissões
Crie usuários pelo `/admin/`. O superusuário é administrador. Para usar permissões por grupo, crie um grupo chamado `Administrador` e atribua-o aos usuários administrativos. Atendentes autenticados podem consultar catálogo, clientes, vendas e entregas; operações de cadastro e perdas são restritas a administradores. Ajuste grupos e permissões antes de uso real.

## PostgreSQL (opcional)
Configure `DATABASE_URL` no ambiente, por exemplo:

```powershell
$env:DATABASE_URL = "postgresql://flora_user:senha@localhost:5432/floraerp"
$env:DJANGO_DEBUG = "False"
$env:DJANGO_SECRET_KEY = "substitua-por-um-segredo-forte"
$env:DJANGO_ALLOWED_HOSTS = "seu-dominio.com"
python manage.py migrate
```

Crie previamente o banco e usuário no PostgreSQL. Para produção, use HTTPS, segredos fora do repositório, backup, armazenamento de mídia apropriado, configuração de e-mail e `python manage.py check --deploy`. O backend PostgreSQL utiliza `psycopg`.

## Módulos incluídos
- Dashboard com indicadores calculados no banco e gráfico de vendas.
- Catálogo, categorias, produtos, ficha botânica e pesquisa na web.
- Clientes, pesquisa e histórico de pedidos.
- PDV com carrinho no navegador, validação no servidor, preço registrado, pagamento e baixa de estoque.
- Kits com composição e baixa de componentes.
- Histórico de vendas, comprovante imprimível e cancelamento com estorno auditável.
- Entregas com validação de datas e status.
- Perdas e avarias com movimentação de estoque.
- Alertas e histórico de movimentações.
- Relatórios com exportação CSV.
- Administração nativa do Django, registro de auditoria e comando de demonstração.
- Testes automatizados básicos para autenticação, vendas, estoque, kits, estorno e validação.

## Observações importantes
- A primeira execução deve gerar migrações locais com `makemigrations`; migrações não são artefatos de banco e devem ser versionadas após geradas.
- O guia de cuidados abre o WhatsApp para revisão manual; o envio é feito pelo usuário.
- Os dados de demonstração são fictícios e nunca devem ser confundidos com dados de clientes reais.
- Antes de produção, complemente a matriz de permissões por operação, teste fluxos completos e revise privacidade, política de retenção, backup e controles de concorrência. SQLite não oferece os mesmos bloqueios de linha que PostgreSQL.
