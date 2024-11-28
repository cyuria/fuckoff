"""Package with shell specific actions, each shell class should
implement `from_shell`, `to_shell`, `app_alias`, `put_to_history` and
`get_aliases` methods.
"""
import os

from pathlib import Path
from psutil import Process
from typing import Dict

from .bash import Bash
from .fish import Fish
from .generic import Generic
from .tcsh import Tcsh
from .zsh import Zsh
from .powershell import Powershell


shells: Dict[str, type[Generic]] = {
    'bash': Bash,
    'fish': Fish,
    'zsh': Zsh,
    'csh': Tcsh,
    'tcsh': Tcsh,
    'powershell': Powershell,
    'pwsh': Powershell,
}


def _get_shell() -> Generic:
    name = Path(
        os.environ.get('FUCKOFF_SHELL') or
        os.environ.get('SHELL') or
        ''
    ).stem
    if name in shells:
        return shells[name]()

    for proc in Process(os.getpid()).parents():
        name = Path(proc.name()).stem
        if name in shells:
            return shells[name]()

    return Generic()


shell = _get_shell()
