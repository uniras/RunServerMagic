# RunServer Magic Command

## 概要

Jypyter(notebook/lab)・VSCodeまたはGoogle ColabでコードセルのPythonコードをサーバーとして起動するマジックコマンドです。

## 使い方

### マジックコマンドの追加

コードセルに以下のコードを貼り付けて実行しマジックコマンドを登録してください。カーネルやランタイムを再起動する度に再実行する必要があります。

```python
%pip install -q runservermagic
from runserver import register_run_server
register_run_server()
```

### マジックコマンドの使い方

コードセルの冒頭に`%%run_server`マジックコマンドを記述してください。実行するとコードセルのコードがサーバーとして実行されます。  
以下はFlaskでHello Worldを表示するサーバーの例です。

```python
%%run_server 8000 flask_app.py

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


app.run(port={{server_port}})
```

`{{server_port}}` はマジックコマンドの引数で指定したポート番号に置き換えられます。

起動したサーバーを停止するには`%stop_server`マジックコマンドを別のコードセルから実行してください。  
同じポート番号でサーバーを起動した場合は、自動的に古いサーバーを停止してから新しいサーバーを起動します。

ノートブック内でサーバーにアクセスしてwebページを表示する場合は、`IPython.display.IFrame`を使用します。  
`server_url`には直前に`%%run server`で起動したサーバーのURLが格納されています。

```python
import IPython

IPython.display.IFrame(src=f"{server_url}/", width="100%", height=500)  # type: ignore
```

### マジックコマンド

#### %%run_server

セル内のPythonコードをサーバーとして起動します。

```jupyter
%%run_server [port] [file] [remove]
```

- `port`: サーバーのポート番号を指定します。デフォルトは `8000` です。
- `file`: サーバーとして起動するために書き出すPythonファイル名を指定します。デフォルトは `server.py` です。
- `remove`: サーバーを起動した後に書き出したファイルを削除するかどうかを指定します。デフォルトは `True` です。

#### %stop_server

起動したサーバーを停止します。

```jupyter
%stop_server [port]
```

- `port`: 停止するサーバーのポート番号を指定します。デフォルトは `8000` です。

## グローバル変数

run_serverマジックコマンドがあるセルを実行した後には以下のグローバル変数が登録されています

- `server_url`: 直前に起動したサーバーのURLが格納されています。
- `server_url_{port番号}`: 指定のポート番号で起動したサーバーのURLが格納されています。
