import logging
from proyecto_1.modules.paths import LOGGS_PATH

def crear_logger():
    # Configuracion del loggger
    logger = logging.getLogger(__name__)
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)

    # handler de consola
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # hander archivos
    fh = logging.FileHandler(filename = LOGGS_PATH, mode = "a", encoding = "utf-8")
    fh.setLevel(logging.INFO)

    # Formato
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d_%H:%M:%S"
    )
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Agregar handlers al logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger

logger = crear_logger()