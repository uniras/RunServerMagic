import sys
import time
import signal
import subprocess

from IPython import get_ipython  # type: ignore


def end_server(server_port: int, message: bool = True) -> None:
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
                        server_process.wait(5)
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


def run_server(args: dict) -> None:
    # 引数を取得
    if not isinstance(args, dict):
        raise ValueError("invalid argument type")
    port_str = args.get("server_port", "8080")
    show_iframe = args.get("show_iframe", "True")
    width_str = args.get("width_str", "500")
    height_str = args.get("height_str", "500")
    server_code_arg = args.get("server_code", "")

    port = port_str if isinstance(port_str, int) else int(port_str) if isinstance(port_str, str) and port_str.isdecimal() else 8080
    py_name = "python" if sys.platform == "win32" else "python3"
    server_code = server_code_arg.strip().replace("{{server_port}}", str(port)) + "\n"

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
    end_server(port, False)

    # サーバーを起動
    print("サーバーを起動しています...")
    server_process = subprocess.Popen(
        [py_name, __file__],
        text=True,
        encoding="utf-8",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    server_process.stdin.write(server_code)
    server_process.stdin.close()

    time.sleep(1)

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

        # show_iframeの値を確認
        if isinstance(show_iframe, bool):
            show_iframe = "true" if show_iframe else "false"
        elif not isinstance(show_iframe, str):
            show_iframe = "true"

        # IFrameを表示
        if show_iframe.lower() == "true":
            import IPython.display as display  # type: ignore
            width = width_str if isinstance(width_str, int) else int(width_str) if isinstance(width_str, str) and width_str.isdecimal() else 500
            height = height_str if isinstance(height_str, int) else int(height_str) if isinstance(height_str, str) and height_str.isdecimal() else 500
            display.display(display.IFrame(src=server_url+"/", width=width, height=height))


# このファイルをPythonインタプリタで開いた場合の処理
def run_main_func() -> None:
    # 標準入力からHTMLを取得
    code = sys.stdin.read()

    exec(code)


if __name__ == "__main__":
    run_main_func()
