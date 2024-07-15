# RunServer Magic Command

## 概要

Jypyter(notebook/lab)・VSCodeまたはGoogle ColabでコードセルのPythonコードをサーバーとして起動するマジックコマンドです。

## 使い方

### マジックコマンドの追加

コードセルに以下のコードを貼り付けて実行しマジックコマンドを登録してください。カーネルやランタイムを再起動する度に再実行する必要があります。

```python
%pip install runservermagic
from runserver import register_run_server
register_run_server()
```

### マジックコマンドの使い方

コードセルの冒頭に以下のようにマジックコマンドを記述してください。実行するとアウトプットにiframeが表示されてその中でコードセルのコードがサーバーとして実行されます。

```python
%%run_server 8000 flask_app.py False

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


app.run(port={{server_port}})
```

`{{server_port}}` はマジックコマンドの引数で指定したポート番号に置き換えられます。

### マジックコマンド

#### %%run_server

セル内のPythonコードをサーバーとして起動します。

```jupyter
%%run_server [port] [file] [remove]
```

- `port`: サーバーのポート番号を指定します。デフォルトは `8000` です。
- `file`: サーバーとして起動するために書き出すPythonファイル名を指定します。デフォルトは `server.py` です。
- `remove`: サーバーを起動した後に書き出したファイルを削除するかどうかを指定します。デフォルトは `True` です。

## グローバル変数

run_serverマジックコマンドがあるセルを実行した後には以下のグローバル変数が登録されています

- `server_url`: 直前に起動したサーバーのURLが格納されています。
- `server_url_{port番号}`: 指定のポート番号で起動したサーバーのURLが格納されています。
