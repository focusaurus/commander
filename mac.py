from builtins import str
from .helpers import run
import logging
import subprocess
import functools
import types

logger = logging.getLogger("commander")


def maestro(scriptId):
    """Run a Keyboard Maestro script by ID (more robust) or name."""
    run(
        """osascript -e 'tell application "Keyboard Maestro Engine" to """
        """do script "%s"'\n""" % scriptId
    )
