# Aura Produções e Eventos

Site publicado em https://auraproducoeseeventos.com.br (Vercel, deploy automático a cada push na `main`).

## Estrutura

| Caminho | O que é |
|---|---|
| `index.html` | Página inicial. É a fonte das páginas de serviço |
| `mobilia-para-eventos.html` e demais | Páginas de serviço (geradas, não editar à mão) |
| `blog/posts/*.md` | **Artigos do blog**: um arquivo Markdown por artigo |
| `blog/*.html`, `blog/feed.xml`, `sitemap.xml` | Gerados pelo script, não editar à mão |
| `docs/modelo-de-post.md` | Modelo para criar um artigo novo |
| `scripts/build.py` | Gera tudo: páginas de serviço, blog, feed RSS e sitemap |

## Publicar um artigo novo

1. Copie `docs/modelo-de-post.md` para `blog/posts/AAAA-MM-DD-nome-curto.md`.
2. Preencha o cabeçalho (`title`, `description`, `slug`, `date`, `service`, `image`) e escreva o texto em Markdown.
3. Mude `draft: true` para `draft: false`.
4. Envie para a `main` (pode ser pelo próprio site do GitHub: *Add file → Create new file*).

O GitHub Action **Publicar blog e páginas** gera o HTML, o sitemap e o feed e salva no repositório; a Vercel publica em seguida.

- **Agendar:** coloque uma `date` futura. O Action roda todo dia de manhã e publica o artigo quando a data chegar.
- **Rascunho:** `draft: true` mantém o arquivo no repositório sem publicar.
- **FAQ no Google:** uma seção `## Perguntas frequentes` com perguntas em `###` vira dados estruturados de FAQ automaticamente.
- **Imagens:** coloque em `img/` (de preferência `.webp`, até ~1600px) e use `/img/arquivo.webp` no campo `image`.
- **`service`:** um destes: `mobilia-para-eventos`, `plataforma-360`, `pequeno-tequileiro`, `story-maker`, `podcast-para-eventos`, `chopeira-movel`. Gera a caixa de contato do serviço no fim do artigo.

## Rodar localmente

```bash
python3 scripts/build.py
```

Sem dependências externas (Python 3.9+). Ao editar o `index.html`, rode o mesmo comando para atualizar as páginas de serviço.
