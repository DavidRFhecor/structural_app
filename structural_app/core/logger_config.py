import logging

def init_logger():
    """Configuración básica del logger para la aplicación."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("structural_app")
    logger.info("Logger inicializado correctamente.")
    return logger