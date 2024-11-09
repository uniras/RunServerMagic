import shlex
import IPython.core.magic as magic  # type: ignore
from runserver.serverrunner import run_server, end_server
from IPython import get_ipython  # type: ignore


@magic.register_cell_magic
def runserv(line: str, cell: str) -> None:
    line_args = shlex.split(line)
    args = {}
    args["server_port"] = line_args[0] if len(line_args) > 0 else "8080"
    args["show_iframe"] = line_args[1] if len(line_args) > 1 else "True"
    args["width_str"] = line_args[2] if len(line_args) > 2 else "500"
    args["height_str"] = line_args[3] if len(line_args) > 3 else "500"
    args["server_code"] = cell

    run_server(args)


@magic.register_line_magic
def endserv(line: str) -> None:
    args = shlex.split(line)
    server_port = int(args[0]) if len(args) > 0 else 8080
    end_server(server_port, True)


def register_run_server() -> None:
    ipython = get_ipython()
    ipython.register_magic_function(runserv)
    ipython.register_magic_function(endserv)
