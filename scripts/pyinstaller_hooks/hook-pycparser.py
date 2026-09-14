"""Override the PyInstaller pycparser hook.

Upstream still hidden-imports ``pycparser.lextab`` and ``pycparser.yacctab``.
pycparser 3.x does not ship those generated modules, so the hook only produces
false-positive "Hidden import not found" warnings. EQGM does not need them:
pywebview → pythonnet → cffi pulls pycparser in, but the tables are unused.
"""

hiddenimports: list[str] = []
