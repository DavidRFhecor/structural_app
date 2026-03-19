import reflex as rx
from reflex.plugins.sitemap import SitemapPlugin # Importación técnica para evitar el warning

config = rx.Config(
    app_name="structural_app",
    # Quitamos el string y usamos la clase directamente
    disable_plugins=[SitemapPlugin],
)