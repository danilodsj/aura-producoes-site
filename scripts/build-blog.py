"""Preview local do blog (o site publicado usa a função api/blog.py na Vercel).

Uso: python3 scripts/build-blog.py [AAAA-MM-DD]
Gera preview/blog/*.html, preview/sitemap.xml e preview/blog/feed.xml como o
site estaria na data informada (padrão: hoje) e valida todos os artigos.
"""
import datetime, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'api' / '_lib'))
import blogcore as core

day = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else core.today()
allp = core.all_posts()
posts = core.published(day)
out = ROOT / 'preview' / 'blog'; out.mkdir(parents=True, exist_ok=True)
for f in out.glob('*.html'): f.unlink()
for p in posts: (out / f"{p['slug']}.html").write_text(core.build_post(p, posts), encoding='utf-8')
(out / 'index.html').write_text(core.build_index(posts), encoding='utf-8')
(out / 'feed.xml').write_text(core.build_feed(posts), encoding='utf-8')
(ROOT / 'preview' / 'sitemap.xml').write_text(core.build_sitemap(posts), encoding='utf-8')
future = sorted(p['date'] for p in allp if p not in posts and not p['draft'])
print(f'{day}: {len(posts)} publicados de {len(allp)}' + (f'; próximo em {future[0]}, último em {future[-1]}' if future else ''))
