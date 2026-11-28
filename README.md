# Aura Produções e Eventos

Site publicado em https://auraproducoeseeventos.com.br (Vercel, deploy automático a cada push na `main`).

## Estrutura

| Caminho | O que é |
|---|---|
| `index.html` | Página inicial. É a fonte das páginas de serviço |
| `mobilia-para-eventos.html` e demais | Páginas de serviço (geradas por `scripts/build.py`) |
| `api/_content/posts/*.md` | **Artigos do blog**: um arquivo Markdown por artigo |
| `api/_content/services.json` | Serviços: nomes, endereços e textos de SEO |
| `api/blog.py` + `api/_lib/blogcore.py` | Função da Vercel que serve `/blog`, `/blog/<artigo>`, `/blog/feed.xml` e `/sitemap.xml` |
| `docs/modelo-de-post.md` | Modelo para criar um artigo novo |

## Como a publicação automática funciona

Todos os artigos ficam salvos na Vercel. A função `api/blog.py` só mostra um artigo
(no blog, no sitemap e no feed) quando a data dele chega, à meia-noite no horário de
Brasília. Não há cron, GitHub Action nem nenhum serviço externo envolvido: o cache da
Vercel expira à meia-noite e o artigo do dia aparece no primeiro acesso.

Artigos com data futura respondem 404 e os arquivos `.md` não são acessíveis pela internet.

## Publicar um artigo novo

1. Copie `docs/modelo-de-post.md` para `api/_content/posts/AAAA-MM-DD-nome-curto.md`.
2. Preencha o cabeçalho (`title`, `description`, `slug`, `date`, `service`, `image`) e escreva o texto em Markdown.
3. Mude `draft: true` para `draft: false`.
4. Envie para a `main` (pode ser pelo próprio site do GitHub: *Add file → Create new file*).

- **Agendar:** use uma `date` futura. O artigo aparece sozinho na data.
- **Rascunho:** `draft: true` mantém o arquivo salvo sem publicar.
- **FAQ no Google:** uma seção `## Perguntas frequentes` com perguntas em `###` vira dados estruturados de FAQ.
- **Imagens:** coloque em `img/` (de preferência `.webp`, até ~1600px) e use `/img/arquivo.webp` no campo `image`.
- **`service`:** um destes: `mobilia-para-eventos`, `plataforma-360`, `pequeno-tequileiro`, `story-maker`, `podcast-para-eventos`, `chopeira-movel`.

## Rodar localmente

```bash
python3 scripts/build.py
```

Regera as páginas de serviço a partir do `index.html` e valida todos os artigos.
Para ver o blog como estará numa data: `python3 scripts/build-blog.py 2026-12-15` (gera `preview/`).
