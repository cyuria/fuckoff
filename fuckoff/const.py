def _genConst(name: str) -> str:
    return u'<const: {}>'.format(name)


KEY_UP = _genConst('↑')
KEY_DOWN = _genConst('↓')
KEY_CTRL_C = _genConst('Ctrl+C')
KEY_CTRL_N = _genConst('Ctrl+N')
KEY_CTRL_P = _genConst('Ctrl+P')

KEY_MAPPING = {'\x0e': KEY_CTRL_N,
               '\x03': KEY_CTRL_C,
               '\x10': KEY_CTRL_P}

ACTION_SELECT = _genConst('select')
ACTION_ABORT = _genConst('abort')
ACTION_PREVIOUS = _genConst('previous')
ACTION_NEXT = _genConst('next')

ALL_ENABLED = _genConst('All rules enabled')
DEFAULT_RULES = [ALL_ENABLED]
DEFAULT_PRIORITY = 1000

DEFAULT_SETTINGS = {'rules': DEFAULT_RULES,
                    'exclude_rules': [],
                    'wait_command': 0.5,
                    'require_confirmation': True,
                    'no_colors': False,
                    'debug': False,
                    'priority': {},
                    'history_limit': None,
                    'alter_history': True,
                    'wait_slow_command': 5,
                    'slow_commands': ['lein', 'react-native', 'gradle',
                                      './gradlew', 'vagrant'],
                    'repeat': False,
                    'instant_mode': False,
                    'num_close_matches': 3,
                    'env': {'LC_ALL': 'C', 'LANG': 'C', 'GIT_TRACE': '1'},
                    'excluded_search_path_prefixes': []}

ENV_TO_ATTR = {'FUCKOFF_RULES': 'rules',
               'FUCKOFF_EXCLUDE_RULES': 'exclude_rules',
               'FUCKOFF_WAIT_COMMAND': 'wait_command',
               'FUCKOFF_REQUIRE_CONFIRMATION': 'require_confirmation',
               'FUCKOFF_NO_COLORS': 'no_colors',
               'FUCKOFF_DEBUG': 'debug',
               'FUCKOFF_PRIORITY': 'priority',
               'FUCKOFF_HISTORY_LIMIT': 'history_limit',
               'FUCKOFF_ALTER_HISTORY': 'alter_history',
               'FUCKOFF_WAIT_SLOW_COMMAND': 'wait_slow_command',
               'FUCKOFF_SLOW_COMMANDS': 'slow_commands',
               'FUCKOFF_REPEAT': 'repeat',
               'FUCKOFF_INSTANT_MODE': 'instant_mode',
               'FUCKOFF_NUM_CLOSE_MATCHES': 'num_close_matches',
               'FUCKOFF_EXCLUDED_SEARCH_PATH_PREFIXES': 'excluded_search_path_prefixes'}

SETTINGS_HEADER = u"""# Fuckoff settings file
#
# The rules are defined as in the example bellow:
#
# rules = ['cd_parent', 'git_push', 'python_command', 'sudo']
#
# The default values are as follows. Uncomment and change to fit your needs.
# See https://github.com/cyuria/fuckoff#settings for more information.
#

"""

ARGUMENT_PLACEHOLDER = 'FUCKOFF_ARGUMENT_PLACEHOLDER'

CONFIGURATION_TIMEOUT = 60

USER_COMMAND_MARK = u'\u200B' * 10

LOG_SIZE_IN_BYTES = 1024 * 1024

LOG_SIZE_TO_CLEAN = 10 * 1024

DIFF_WITH_ALIAS = 0.5

SHELL_LOGGER_SOCKET_ENV = 'SHELL_LOGGER_SOCKET'

SHELL_LOGGER_LIMIT = 5
