import time
import subprocess
import sys
import signal
import os
import shlex

from IPython import get_ipython  # type: ignore
import IPython.core.magic as magic  # type: ignore


def stop_server_func(server_port: int, message: bool = False) -> None:
    # プラットフォームによってシグナルの種類を変更
    termsignal = signal.CTRL_C_EVENT if sys.platform == "win32" else signal.SIGTERM

    # IPythonのユーザー名前空間を取得
    userns = get_ipython().user_ns

    if "server_process_list" in userns:
        server_process_list = userns["server_process_list"]
        if str(server_port) in server_process_list:
            server_process = server_process_list[str(server_port)]
            if server_process.poll() is None:
                print("サーバーを停止しています...")
                try:
                    server_process.send_signal(termsignal)
                    try:
                        server_process.wait(10)
                    except subprocess.TimeoutExpired:
                        server_process.kill()
                        time.sleep(5)
                except: # noqa
                    pass
            server_process_list.pop(str(server_port))
        else:
            if message:
                print("サーバーが起動していません。")
    else:
        if message:
            print("サーバーが起動していません。")
        server_process_list = {}

    userns["server_process_list"] = server_process_list


def run_server_func(args: dict) -> None:
    # 引数を取得
    if not isinstance(args, dict):
        raise ValueError("invalid argument type")
    port_str = args.get("server_port", "8080")
    server_file = args.get("server_file", "server.py")
    remove_file = args.get("remove_file", "False").lower()
    show_iframe = args.get("show_iframe", "False").lower()
    width_str = args.get("width_str", "500")
    height_str = args.get("height_str", "500")

    port = port_str if isinstance(port_str, int) else int(port_str) if isinstance(port_str, str) and port_str.isdecimal() else 8080
    py_name = "python " if sys.platform == "win32" else "exec python3 "

    # Colab環境であるかどうかを判定
    try:
        from google.colab.output import eval_js  # type: ignore
        is_colab = True
    except ImportError:
        is_colab = False

    # サーバーのURLを取得
    if is_colab:
        server_url = eval_js(f"google.colab.kernel.proxyPort({port})").strip("/")
    else:
        server_url = f"http://localhost:{port}"

    # 以前に起動したサーバーを停止
    stop_server_func(port)

    # サーバーを起動
    print("サーバーを起動しています...")
    server_process = subprocess.Popen(
        py_name + server_file,
        encoding="utf-8",
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    time.sleep(5)

    if remove_file == "true":
        os.remove(server_file)

    if server_process.poll() is not None:
        print("サーバーを起動できませんでした。")
        print(server_process.stdout.read())
        print(server_process.stderr.read())
    else:
        # IPythonのユーザー名前空間を取得
        userns = get_ipython().user_ns
        server_process_list = userns["server_process_list"]
        server_process_list[str(port)] = server_process
        userns["server_process_list"] = server_process_list
        userns["server_url"] = server_url
        userns["server_url_" + str(port)] = server_url
        print("サーバーを起動しました。")
        print(f"URL: {server_url}")

        # IFrameを表示
        if show_iframe == "true":
            import IPython.display as display  # type: ignore
            width = width_str if isinstance(width_str, int) else int(width_str) if isinstance(width_str, str) and width_str.isdecimal() else 500
            height = height_str if isinstance(height_str, int) else int(height_str) if isinstance(height_str, str) and height_str.isdecimal() else 500
            print("IFrameを表示しています...")
            display.display(display.IFrame(src=server_url+"/", width=width, height=height))


@magic.register_cell_magic
def run_server(line: str, cell: str) -> None:
    line_args = shlex.split(line)
    args = {}
    args["server_port"] = line_args[0] if len(line_args) > 0 else "8080"
    args["server_file"] = line_args[1] if len(line_args) > 1 else "server.py"
    args["remove_file"] = line_args[2] if len(line_args) > 2 else "True"
    args["show_iframe"] = line_args[3] if len(line_args) > 3 else "False"
    args["width_str"] = line_args[4] if len(line_args) > 4 else "500"
    args["height_str"] = line_args[5] if len(line_args) > 5 else "500"

    cell = cell.strip().replace("{{server_port}}", args["server_port"]) + "\n"

    with open(args["server_file"], "w", encoding="utf-8") as f:
        f.write(cell)

    run_server_func(args)


@magic.register_line_magic
def stop_server(line: str) -> None:
    args = shlex.split(line)
    server_port = int(args[0]) if len(args) > 0 else 8080
    stop_server_func(server_port, True)


def register_run_server() -> None:
    ipython = get_ipython()
    ipython.register_magic_function(run_server)
    ipython.register_magic_function(stop_server)
