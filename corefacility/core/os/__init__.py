from .command_maker import CommandMaker


def _check_os_posix():
    try:
        import posix
    except ImportError:
        raise RuntimeError("This code can't be executed in non-POSIX operating system")
