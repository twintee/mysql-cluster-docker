#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
from os.path import join, dirname, abspath, isfile, isdir
import argparse
import helper as fn
from time import sleep

dir_scr = abspath(dirname(__file__))
os.chdir(dir_scr)

file_env = join(dir_scr, ".env")

def main(_args):
    """
    initialize container
    """

    # コンテナ削除
    cmd_down = "docker-compose down -v"
    for line in fn.cmdlines(_cmd=cmd_down):
        sys.stdout.write(line)

    envs = fn.getenv(file_env)
    node = envs['NODE']
    if not _args.node is None:
        node = _args.node
    if node == "":
        fn.error("node type not set.")
        sys.exit()
    fn.info("run {node} node.")

    target = ""
    if node != "all":
        target = f"db-{node}"

    # サービス作成
    for line in fn.cmdlines(_cmd=f"docker-compose up -d {target}", _encode="utf8"):
        sys.stdout.write(line)

    if target != "db-slave":

        initialized = False
        while initialized:
            fn.info(f"waiting 1sec for init {node} node...")
            sleep(1)
            for line in fn.cmdlines(_cmd=f"docker-compose logs db-master", _encode="utf8"):
                if "999_finish.sql" in line:
                    initialized = True

    # パーミッション調整
    nodes = ["node-mysql-master", "node-mysql-slave"]
    if node != "all":
        nodes = [f"node-mysql-{node}"]
    for ref in nodes:
        for line in fn.cmdlines(_cmd=f"docker exec -it {ref} chmod -R 664 /etc/mysql/conf.d"):
            sys.stdout.write(line)
        for line in fn.cmdlines(_cmd=f"docker exec -it {ref} chmod -R 664 /tmp/common/opt"):
            sys.stdout.write(line)
        # fn.rmdir(join(dir_scr, "vol", node, "data"), True)
    # サービス作成
    for line in fn.cmdlines(_cmd=f"docker-compose restart {target}"):
        sys.stdout.write(line)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='set env params')
    parser.add_argument('node', help="set generate node type. 'master' or 'slave' or 'all'")
    args = parser.parse_args()

    if not args.node is None:
        if not args.node in ["master", "slave", "all"]:
            fn.info("[info] args error.")

    if not isfile(file_env):
        fn.error(f"""not exist .env file.\nexecute script. [ python3 config.py ]""")

    if not fn.input_yn("initialize container. ok? (y/*) :"):
        fn.info("initialize canceled.")
        sys.exit()

    fn.info("initialize start.")
    main(args)
    fn.info("initialize end.")
