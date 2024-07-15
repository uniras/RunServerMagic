import time
import subprocess
import sys
import signal
import os
import shlex

from IPython import get_ipython  # type: ignore
import IPython.core.magic as magic  # type: ignore


def stop_server_func(server_port: int) -> None:
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
        server_process_list = {}

    userns["server_process_list"] = server_process_list


def run_server_func(server_port: int, server_file: str, remove_file: str) -> None:
    # プラットフォームによってPythonコマンドを変更
    py_name = "python" if sys.platform == "win32" else "python3"

    # Colab環境ではpopenの引数にshell=Trueを指定するとうまくいかない？
    try:
        from google.colab.output import eval_js  # type: ignore
        is_colab = True
        shell_flag = False
    except ImportError:
        is_colab = False
        shell_flag = True

    # サーバーのURLを取得
    if is_colab:
        server_url = eval_js(f"google.colab.kernel.proxyPort({server_port})").strip("/")
    else:
        server_url = f"http://localhost:{server_port}"

    # 以前に起動したサーバーを停止
    stop_server_func(server_port)

    # サーバーを起動
    print("サーバーを起動しています...")
    server_process = subprocess.Popen(
        [py_name, server_file],
        shell=shell_flag,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    time.sleep(5)

    if remove_file.lower() == "true":
        os.remove(server_file)

    if server_process.poll() is not None:
        print("サーバーを起動できませんでした。")
        print(server_process.stdout.read())
        print(server_process.stderr.read())
    else:
        # IPythonのユーザー名前空間を取得
        userns = get_ipython().user_ns
        server_process_list = userns["server_process_list"]
        server_process_list[str(server_port)] = server_process
        userns["server_process_list"] = server_process_list
        userns["server_url"] = server_url
        userns["server_url_" + str(server_port)] = server_url
        print("サーバーを起動しました。")
        print(f"URL: {server_url}")


@magic.register_cell_magic
def run_server(line: str, cell: str) -> None:
    args = shlex.split(line)
    server_port = int(args[0]) if len(args) > 0 else 8080
    server_file = args[1] if len(args) > 1 else "server.py"
    remove_file = args[2] if len(args) > 2 else "True"

    cell = cell.strip().replace("{{server_port}}", str(server_port))

    with open(server_file, "w") as f:
        f.write(cell)

    run_server_func(server_port, server_file, remove_file)


@magic.register_line_magic
def stop_server(line: str) -> None:
    args = shlex.split(line)
    server_port = int(args[0]) if len(args) > 0 else 8080
    stop_server_func(server_port)


def register_run_server() -> None:
    ipython = get_ipython()
    ipython.register_magic_function(run_server)
    ipython.register_magic_function(stop_server)
