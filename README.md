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
- **Interface responsiva** com Bootstrap 5 e dois temas visuais à escolha (veja [Temas](#temas))
- **Vídeo do YouTube** opcional em cada post: na lista, toca sem som quando o mouse passa sobre a capa; na página do post, aparece o player (pacote `django-embed-video`)
- **Comentários** em cada post: só usuários logados comentam (até 500 caracteres); o autor do comentário e o dono do post podem apagá-lo
- **Página Contact** com formulário (nome, e-mail e mensagem opcional) e campo-isca anti-robô; as mensagens são lidas no `/admin` (nenhum e-mail é enviado)
- **Página About** com apresentação do autor e do projeto
- **Faixa de redes sociais** no topo (Instagram, Facebook, TikTok e LinkedIn), com os links configurados pelo `.env`

## Tecnologias

| Camada | Tecnologia |
| --- | --- |
| Backend | Python, Django 5.2 |
| Banco de dados | PostgreSQL (driver `psycopg` 3) |
| Frontend | Templates Django, Bootstrap 5.3, Bootstrap Icons |
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
| `SOCIAL_INSTAGRAM_URL`, `SOCIAL_FACEBOOK_URL`, `SOCIAL_TIKTOK_URL`, `SOCIAL_LINKEDIN_URL` | Links das redes sociais na faixa do topo (opcionais; vazio deixa o link como `#`) |
| `SITE_THEME` | Tema visual: `magic` (padrão) ou `classic`; veja [Temas](#temas) |

Para gerar uma `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

## Temas

O visual é escolhido pela variável `SITE_THEME` no `.env`. Os dois temas convivem no projeto,
então trocar de um para o outro não apaga nada.

| Valor | Visual |
| --- | --- |
| `magic` (padrão) | Pergaminho, bordô e dourado, com tipografia Almendra e EB Garamond, inspirado em Harry Potter |
| `classic` | Bege e marrom, com tipografia Cormorant Garamond e EB Garamond |

O tema `magic` tem dois modos, trocados pelo botão do menu e lembrados no navegador:

- **Lumos** (claro) e **Nox** (escuro). Ao ir para o Nox, as velas do teto se apagam uma a uma, da direita para a
  esquerda, deixando uma brasa no pavio; ao voltar para o Lumos, acendem da esquerda para a direita.
- **Cursor de varinha**, com a ponta acesa sobre links e botões. No Nox, uma aura branca ilumina o entorno
  quando o mouse está sobre algo clicável.
- **Rastro de faíscas** atrás do mouse e **cartas**: as mensagens do sistema chegam como correio e as de sucesso
  somem sozinhas.
- O botão **Turn effects off**, no rodapé, desliga velas, varinha, aura e faíscas. Quem pede menos animação ao
  sistema já recebe a página sem movimento.

### Casas, pomo de ouro e Patrono (tema `magic`)

- **Chapéu Seletor**: o botão do menu abre um teste de 5 perguntas. A casa (Gryffindor, Slytherin, Hufflepuff ou
  Ravenclaw) é guardada no navegador e muda as cores do site, nos modos Lumos e Nox.
- **Casa por post**: ao criar ou editar um post, o autor pode escolher uma casa. Quem abre o post vê a página nas
  cores dela, com uma faixa avisando; ao sair, volta para o tema escolhido no teste.
- **Pomo de ouro**: voa pela tela e pode ser apanhado com um clique; o contador fica no rodapé.
- **Patrono**: um animal de luz atravessa a tela ao publicar um post ou ao clicar em "Expecto Patronum".
- "Turn effects off" e a opção de reduzir movimento do sistema desligam o pomo, o Patrono e a onda de cor.

Depois de atualizar o código, rode `python manage.py migrate` (o campo `house` do post é novo).

> Harry Potter é marca e obra protegidas. O tema é "inspirado em": usa cores, fontes livres e desenhos próprios,
> sem logotipos, brasões, imagens ou textos oficiais. Se for publicar o blog, mantenha assim.

## Testes

```bash
python manage.py test
```

A suíte cobre geração de slug, validações do formulário, visibilidade de rascunhos,
cadastro/login/logout, paginação, as regras de permissão de edição e exclusão e os dois temas visuais e as casas do tema `magic`.
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
│   ├── context_processors.py  # Redes sociais, tema ativo e velas, disponíveis em todos os templates
│   ├── tests.py       # Testes automatizados
│   ├── templates/     # Templates e partials reutilizáveis
│   └── static/blog/   # css/ (style.css = base e tema classic, magic.css = tema magic, houses.css = casas), js/ (magic.js, houses.js), img/ (cursores)
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
