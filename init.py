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

def main():
    """
    initialize container
    """

    # コンテナ削除
    cmd_down = "docker-compose down -v"
    for line in fn.cmdlines(_cmd=cmd_down):
        sys.stdout.write(line)

    envs = fn.getenv(file_env)
    node = envs['NODE']
    if node == "":
        fn.error("node type not set.")
        sys.exit()
    fn.info(f"run {node} node.")

    target = ""
    if node != "all":
        target = f"db-{node}"

    # サービス作成
    for line in fn.cmdlines(_cmd=f"docker-compose up -d {target}", _encode="utf8"):
        sys.stdout.write(line)

    # サービス起動は若干時間がかかる
    check_node = "db-master"
    if node == "slave":
        check_node = "db-slave"
    fn.info(f"check boot status. [docker-compose logs {check_node}]")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='set env params')
    parser.add_argument('--yes', '-y', help="(option) response 'y' to all input.", action='store_true')
    args = parser.parse_args()

    if not isfile(file_env):
        fn.error(f"""not exist .env file.\nexecute script. [ python3 config.py ]""")

    if not fn.input_yn("initialize container. ok? (y/*) :", args.yes):
        fn.info("initialize canceled.")
        sys.exit()

    fn.info("initialize start.")
    main()
    fn.info("initialize end.")
