# DjangoBlog

Plataforma de blog multiusuário desenvolvida com **Django 5**, **PostgreSQL** e **Bootstrap 5**.
Usuários criam conta, escrevem posts com imagem de capa, salvam rascunhos e gerenciam apenas o que é seu.

> Projeto acadêmico desenvolvido por [Thalyson Alves](https://github.com/alvesthalyson).

<!-- Adicione aqui 2 ou 3 screenshots: ![Home](docs/screenshots/home.png) -->

## Funcionalidades

- **Autenticação completa**: cadastro (com e-mail obrigatório), login, logout e redefinição de senha por e-mail
- **CRUD de posts** com slug único gerado automaticamente a partir do título
- **Rascunhos**: posts com status `draft` só são visíveis para o próprio autor
- **Permissões**: somente o autor pode editar ou excluir seus posts (os demais recebem uma página 403 personalizada)
- **Imagem de capa** com validação (JPG/PNG/WEBP, máx. 5 MB), redimensionamento automático para 800×800 e remoção do arquivo ao excluir o post
- **Paginação** na lista de posts e em "My Posts"
- **Categorias e tags** gerenciadas pelo painel administrativo
- **Páginas de erro** 403, 404 e 500 personalizadas
- **Interface responsiva** com Bootstrap 5

## Tecnologias

| Camada | Tecnologia |
| --- | --- |
| Backend | Python, Django 5.2 |
| Banco de dados | PostgreSQL (driver `psycopg` 3) |
| Frontend | Templates Django, Bootstrap 5.3 |
| Arquivos estáticos | WhiteNoise |
| Imagens | Pillow |
| Desenvolvimento | django-debug-toolbar (somente com `DEBUG=True`) |

## Como executar localmente

Pré-requisitos: Python 3.10+ e PostgreSQL em execução.

```bash
# 1. Clonar e entrar na pasta
git clone https://github.com/alvesthalyson/djangoblog.git
cd djangoblog

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env             # Windows: copy .env.example .env
# edite o .env com sua SECRET_KEY e os dados do PostgreSQL

# 5. Criar as tabelas e um superusuário
python manage.py migrate
python manage.py createsuperuser

# 6. Iniciar o servidor
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` (site) e `http://127.0.0.1:8000/admin/` (painel administrativo).

### Variáveis de ambiente

| Variável | Descrição |
| --- | --- |
| `SECRET_KEY` | Chave secreta do Django (**obrigatória**) |
| `DEBUG` | `True` em desenvolvimento; qualquer outro valor desativa |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por vírgula |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Conexão com o PostgreSQL |

Para gerar uma `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

## Testes

```bash
python manage.py test
```

A suíte cobre geração de slug, validações do formulário, visibilidade de rascunhos,
cadastro/login/logout, paginação e as regras de permissão de edição e exclusão.
(O usuário do PostgreSQL precisa de permissão para criar o banco de testes.)

## Estrutura do projeto

```
djangoblog/
├── config/            # Configurações do projeto (settings, urls, wsgi/asgi)
├── blog/
│   ├── models.py      # Post, Category, Tag
│   ├── views.py       # Views baseadas em classes (CRUD) + handlers de erro
│   ├── forms.py       # PostForm e RegisterForm com validações
│   ├── signals.py     # Remove a imagem de capa ao excluir o post
│   ├── admin.py       # Configuração do painel administrativo
│   ├── tests.py       # Testes automatizados
│   ├── templates/     # Templates e partials reutilizáveis
│   └── static/        # CSS
├── .env.example
├── manage.py
└── requirements.txt
```

## Próximos passos

- Filtro de posts por categoria e tag
- Busca por título e conteúdo
- Comentários nos posts
- Deploy em produção (ex.: Render ou Railway) com envio real de e-mails

## Licença

Projeto de uso educacional.
