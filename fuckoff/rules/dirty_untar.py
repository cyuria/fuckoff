import tarfile
import os

from fuckoff.shells import shell
from fuckoff.utils import for_app


tar_extensions = ('.tar', '.tar.Z', '.tar.bz2', '.tar.gz', '.tar.lz',
                  '.tar.lzma', '.tar.xz', '.taz', '.tb2', '.tbz', '.tbz2',
                  '.tgz', '.tlz', '.txz', '.tz')


def _is_tar_extract(cmd):
    if '--extract' in cmd:
        return True

    cmd = cmd.split()

    return len(cmd) > 1 and 'x' in cmd[1]


def _tar_file(cmd):
    for c in cmd:
        for ext in tar_extensions:
            if c.endswith(ext):
                return (c, c[0:len(c) - len(ext)])


@for_app('tar')
def match(command):
    return ('-C' not in command.script
            and _is_tar_extract(command.script)
            and _tar_file(command.script_parts) is not None)


def get_new_command(command):
    tar_file = _tar_file(command.script_parts)
    if tar_file is None:
        return []
    return [shell.and_('mkdir -p {dir}', '{cmd} -C {dir}') \
        .format(dir=shell.quote(tar_file[1]), cmd=command.script)]


def side_effect(old_cmd, _):
    tar_file = _tar_file(old_cmd.script_parts)
    if tar_file is None:
        return
    with tarfile.TarFile(tar_file[0]) as archive:
        for file in archive.getnames():
            if not os.path.abspath(file).startswith(os.getcwd()):
                # it's unsafe to overwrite files outside of the current directory
                continue

            try:
                os.remove(file)
            except OSError:
                # does not try to remove directories as we cannot know if they
                # already existed before
                pass
