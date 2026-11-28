# Aura Produções e Eventos

Site publicado em https://auraproducoeseeventos.com.br (Vercel, deploy automático a cada push na `main`).

## Páginas

- `index.html`: página inicial (fonte de todas as outras)
- Uma página por serviço: `mobilia-para-eventos`, `plataforma-360`, `pequeno-tequileiro`, `story-maker`, `podcast-para-eventos`, `chopeira-movel`

## Ao editar o site

Edite só o `index.html` e depois rode:

```bash
python3 scripts/build-pages.py
```

O script recria as 6 páginas de serviço e o `sitemap.xml` a partir do `index.html`. Títulos, descrições e textos de SEO de cada serviço ficam em `scripts/build-pages.py`.
