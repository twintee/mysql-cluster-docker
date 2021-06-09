#! /usr/bin/env python
# -*- coding: utf-8 -*-

from json import dump
import os
import sys
from os.path import join, dirname, abspath, isfile, isdir, splitext, basename
import argparse

dir_scr = abspath(dirname(__file__))
dir_base = join(dir_scr, "..", "..", "..")
sys.path.append(dir_base)
import helper as fn
from rep import replicator as rp

os.chdir(dir_scr)
file_env = join(dir_scr, ".env")

def main(_args):
    """
    initialize container
    """
    env_dst = join(dir_scr, "..", '.env')
    envs = fn.getenv(env_dst)

    node = envs["NODE"]
    if not _args.node is None:
        node = _args.node
    if node == "":
        print(f"[error] node type not set.")
        sys.exit()
    container = f"node-mysql-{node}"

    dk_cmd = f"docker exec -it {container}"
    mysql_cmd = f"{dk_cmd} mysql {envs['OPTROOT']}"

    master_host = f"{envs['MASTER_HOST']} : {envs['MASTER_PORT']}"
    # アタッチ処理
    if node == "slave":

        if fn.input_yn(f"\nattach to master[ {master_host} ]. ok? (y/*) :"):
            print(f"\n---------- attach to [ {master_host} ] start")
            cmd = f"{mysql_cmd} -e \"\
CHANGE MASTER TO \
{envs['REP_FILE']}, \
{envs['REP_POS']}, \
MASTER_HOST='{envs['MASTER_HOST']}', \
MASTER_PORT={envs['MASTER_PORT']}, \
MASTER_USER='rep', \
MASTER_PASSWORD='{envs['MYSQL_REP_PASSWORD']}';\
\""
            for line in rp.cmdrun(_cmd=[cmd], _encode="utf8"):
                sys.stdout.write(line)

            cmds = [
                f"{dk_cmd} bash -c \"mysql {envs['OPTROOT']} -e 'START SLAVE;'\"",
            ]
            for line in rp.cmdrun(_cmd=cmds, _encode="utf8"):
                sys.stdout.write(line)
    else:
        print(f"[error] node type error.")
        sys.exit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='set env params')
    parser.add_argument('--file', '-f', help="(option) force set log_file instead of .env")
    parser.add_argument('--pos', '-p', help="(option) force set log_position instead of .env")
    parser.add_argument('--node', '-n', help="(option) if not set dump_path, dump generate from node container. 'master' or 'slave'")
    args = parser.parse_args()

    if not args.node is None:
        if not args.node in ["master", "slave"]:
            fn.error("args error.")
            sys.exit()

    fn.info("initialize start.")
    main(args)
    fn.info("initialize end.")
