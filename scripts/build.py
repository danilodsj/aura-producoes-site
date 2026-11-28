"""Gera tudo: páginas de serviço, blog, feed e sitemap. Uso: python3 scripts/build.py"""
import runpy, pathlib
d = pathlib.Path(__file__).resolve().parent
runpy.run_path(str(d / 'build-pages.py'), run_name='__main__')
runpy.run_path(str(d / 'build-blog.py'), run_name='__main__')
