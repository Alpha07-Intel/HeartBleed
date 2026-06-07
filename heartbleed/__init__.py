from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("heartbleed-osint")
except PackageNotFoundError:
    # package is not installed
    __version__ = "0.3.0"
