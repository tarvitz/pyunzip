"""

Curses Celery Event Viewer.

"""
from celery.bin.celeryctl import celeryctl, Command as _Command

from apps.djcelery import __version__
from apps.djcelery.management.base import CeleryCommand

# Django hijacks the version output and prints its version before our
# version. So display the names of the products so the output is sensible.
_Command.version = "celery %s\ndjango-celery %s" % (_Command.version,
                                                    __version__)


class Command(CeleryCommand):
    """Run the celery control utility."""
    help = "celery control utility"

    def run_from_argv(self, argv):
        util = celeryctl()
        util.execute_from_commandline(argv[1:])
