"""Função da Vercel que serve o blog, o feed RSS e o sitemap.

Cada artigo em api/_content/posts/ só aparece quando a data dele chega
(meia-noite, horário de Brasília). Não depende de GitHub, cron ou Claude.
"""
import os, sys, re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '_lib'))
import blogcore as core  # noqa: E402


def not_found():
    body = ('<main class="wrap"><div class="article"><span class="eyebrow">Erro 404</span>'
            '<h1>Página não encontrada</h1><p>Esse conteúdo não existe ou ainda não foi publicado.</p>'
            '<p><a href="/blog">Ver todos os artigos do blog</a></p></div></main>')
    return core.page('Página não encontrada | Aura', 'Página não encontrada.', core.SITE + '/blog', body,
                     {"@context": "https://schema.org", "@type": "WebPage", "name": "Página não encontrada"}).replace('content="index, follow, max-image-preview:large"', 'content="noindex"')


class handler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self._serve(head=True)

    def do_GET(self):
        self._serve()

    def _serve(self, head=False):
        q = parse_qs(urlparse(self.path).query)
        kind = (q.get('kind') or ['index'])[0]
        slug = (q.get('slug') or [''])[0]
        posts = core.published()
        status, ctype = 200, 'text/html; charset=utf-8'
        try:
            if kind == 'sitemap':
                body, ctype = core.build_sitemap(posts), 'application/xml; charset=utf-8'
            elif kind == 'feed':
                body, ctype = core.build_feed(posts), 'application/rss+xml; charset=utf-8'
            elif kind == 'post':
                post = next((p for p in posts if p['slug'] == slug), None) if re.fullmatch(r'[a-z0-9-]{1,120}', slug) else None
                if post:
                    body = core.build_post(post, posts)
                else:
                    status, body = 404, not_found()
            else:
                body = core.build_index(posts)
        except SystemExit as e:  # erro em algum arquivo .md: não derruba o site, mostra 500
            status, body, ctype = 500, f'Erro no conteúdo do blog: {e}', 'text/plain; charset=utf-8'
        data = body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        cache = core.seconds_to_midnight() if status == 200 else 300
        self.send_header('Cache-Control', f'public, max-age=0, s-maxage={cache}, stale-while-revalidate=60')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        if not head:
            self.wfile.write(data)
