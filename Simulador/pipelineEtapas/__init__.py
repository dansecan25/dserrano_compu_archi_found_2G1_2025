# __init__.py – inicialización del paquete 'componentes'

from .Decode import Decode
from .RegisterFile import RegisterFile
from .Fetch import Fetch
from .Execute import Execute
from .EtapaStore import EtapaStore

__all__ = [
    "Decode",
    "RegisterFile",
    "Fetch",
    "Execute",
    "EtapaStore",
]
