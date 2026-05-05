from importlib.metadata import version, PackageNotFoundError
from .project import ScrivenerProject

try:
    __version__ = version("scrivener-assistant")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__all__ = ["ScrivenerProject", "__version__"]
