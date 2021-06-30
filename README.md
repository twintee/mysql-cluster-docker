# docker-mysql-cluster

## 📚 概要
私用で作ったmysql8系のクラスタノード作成用docker-composeとその他諸々  
基本pythonでコンテナの外から制御したい  

## 🌏 検証環境
- ubuntu :20.04lts

## ⚙ 使用法
- ノード生成
    1. ノード設定スクリプト `config.py`
        応答で必要情報を.envに書き出したりmysql用confやログインパスワードファイルを生成する。  
        - masterを作る場合  
        `python3 config.py master`  
        - slaveを作る場合  
        `python3 config.py slave`  
        - 1master/slaveを個別設定（１ホストクラスタ等）の場合はmaster・slaveの両方実行
    1. (初回のみ)イメージ作成  
        `docker-compose build`
    1. (任意)sqlの初期データの追加  
        - `./mnt/sh_init/`の`masetr`と`slave`にdumpその他データを入れておけばコンテナ生成時にデータが追加される。  
        (ファイル名昇順で実施されるため注意。基本はナンバリングで管理が無難)  
        * エクセルで初期テーブルのsqlファイル作成  
            - `./mnt/sh_init/constants.xlsm`のを編集してマクロ実行でテーブル作成`.sql`とfastapi用のvalidator`.py`を作成可能。  
    1. コンテナ生成
        `python3 init.py`  
        - 応答は基本'y'でボリュームやlogの削除は都度判断。dumpはスクリプトから制御しない。
        - nodeの種類を切り替えたい場合`config.py`を事前に実行してから、生成スクリプトを実行。
        - 1ホストでmaster/slave構成したい場合  
        `python3 init.py all`  

- ダンプ・リストア
    - ダンプ作成  
        `sudo python3 rep/dump.py`  
        - 1ホストクラスタの場合は下記のようにオプションでnode強制  
            `sudo python3 rep/dump.py -n master`  
            - オプション  
                - `--all` or `-a`: `--all-databases`でdump作成  
                - `--compress` or `-c`: 作成されたdumpのzip圧縮ファイルも作成  
                - `--node` or `-n`: 1ホストクラスタ時に使用。ノード強制  
    - リストア(レプリケーションのデタッチ・アタッチ処理兼用)  
        `python3 rep/restore.py`  
        - 1ホストクラスタの場合は下記のようにオプションでnode強制  
            `python3 rep/restore.py -n slave`  
        - slaveノードで実施した場合のみデタッチとアタッチリストアの前後に実施される  
    - (slave限定)デタッチ  
        `python3 rep/detach.py`  
        - オプション  
            - `--node` or `-n`: 1ホストクラスタ時に使用。ノード強制  
    - (slave限定)アタッチ  
        `python3 rep/attach.py`  
        - オプション  
            - `--file` or `-f`: ログファイル指定  
            - `--pos` or `-p`: ログポジション指定  
            - `--node` or `-n`: 1ホストクラスタ時に使用。ノード強制  

## 💨 お手軽１ホストクラスタ構築
- ノード作成
    `python3 config.py master`  
    すべてenterで完了  
    `sudo python3 init.py -n all`  
    すべてyで完了  
    `sudo python3 rep/dump.py -n master`  
    すべてyで完了  
    `sudo cp -r vol/master/dump/{任意のdump} vol/slave/dump` 
    `python3 rep/restore.py -n slave`  
    上記でコピーしたdumpを指定  
    masterにattachするか聞かれたらy
