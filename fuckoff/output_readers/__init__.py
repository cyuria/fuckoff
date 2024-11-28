from typing import Optional
from ..conf import settings
from . import read_log, rerun, shell_logger


def get_output(script: str, expanded: str) -> Optional[str]:
    """Get output of the script."""
    if shell_logger.is_available():
        return shell_logger.get_output(script)
    elif settings.instant_mode:
        return read_log.get_output(script)
    else:
        return rerun.get_output(script, expanded)
