# SQL convert tool (SQL Query Hasher)

SQL Query Hasherは、与えられたSQLクエリのカラム名をハッシュ化して、元のカラム名とのマッピングを提供するPythonツールです。このツールはコマンドラインから直接呼び出すことができます。

## 使用環境

* Pythonバージョン: 3.10
* 使用ライブラリ:
  * sqlparse: SQLのパースに使用

## インストール手順

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