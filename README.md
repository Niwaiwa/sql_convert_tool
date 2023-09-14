# SQL convert tool (SQL Query Hasher)

SQL Query Hasherは、与えられたSQLクエリのカラム名をハッシュ化して、元のカラム名とのマッピングを提供するPythonツールです。このツールはコマンドラインから直接呼び出すことができます。

## 必要な環境

* Pythonバージョン: 3.8以上
* 必要なライブラリ:
  * sqlparse: SQLのパースに使用
  * hashlib: カラム名のハッシュ化に使用

## インストール手順

リポジトリをクローンまたはダウンロードします。

```bash
git clone [リポジトリのURL]
```

プロジェクトディレクトリに移動します。

```bash
cd [プロジェクトのディレクトリ名]
```

必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

## 使い方

コマンドラインから以下のように使用します：

```bash
python main.py "${SQL}"
```

ここで ${SQL} はハッシュ化したいSQLクエリを指します。

例：

```bash
python main.py "SELECT col1, col2 FROM table_name"
```

## テスト

テストは以下のコマンドで実行できます：

```bash
pytest -q tests/*
```