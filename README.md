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

コードセルの冒頭に`%%runserv`マジックコマンドを記述してください。実行するとコードセルのコードがサーバーとして実行されます。  
以下はFlaskでHello Worldを表示するサーバーの例です。

実行するとサーバーを起動し、IFrameでサーバーにアクセスし出力されたwebページを表示します。

```python
%%runserv 8000

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


app.run(port={{server_port}})
```

`{{server_port}}` はマジックコマンドの引数で指定したポート番号に置き換えられます。

起動したサーバーを停止するには`%endserv`マジックコマンドを別のコードセルから実行してください。  
同じポート番号でサーバーを起動した場合は、自動的に古いサーバーを停止してから新しいサーバーを起動します。

別のセルから`IPython.display.IFrame`を使用してwebページを表示することもできます。`server_url`には直前に`%%runserv`で起動したサーバーのURLが格納されています。

```python
import IPython

IPython.display.IFrame(src=f"{server_url}/", width="100%", height=500)  # type: ignore
```

### マジックコマンド

#### %%runserv

セル内のPythonコードをサーバーとして起動します。

```jupyter
%%runserv [port] [show_iframe] [width] [height]
```

- `port`: サーバーのポート番号を指定します。デフォルトは `8000` です。
- `show_iframe`: 起動したサーバーにアクセスするIFrameを表示するかどうかを指定します。デフォルトは `False` です。
- `width`: IFrameの幅を指定します。デフォルトは `500` です。
- `height`: IFrameの高さを指定します。デフォルトは `500` です。

#### %endserv

起動したサーバーを停止します。

```jupyter
%endserv [port]
```

- `port`: 停止するサーバーのポート番号を指定します。デフォルトは `8000` です。

## グローバル変数

run_serverマジックコマンドがあるセルを実行した後には以下のグローバル変数が登録されています

- `server_url`: 直前に起動したサーバーのURLが格納されています。
- `server_url_{port番号}`: 指定のポート番号で起動したサーバーのURLが格納されています。
