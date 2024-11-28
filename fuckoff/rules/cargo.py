def match(command):
    return command.script == 'cargo'


def get_new_command(_):
    return 'cargo build'
