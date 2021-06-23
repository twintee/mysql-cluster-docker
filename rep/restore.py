#! /usr/bin/env python
# -*- coding: utf-8 -*-

from json import dump
import os
import sys
from os.path import join, dirname, abspath, isfile, isdir, splitext, basename
import argparse

dir_scr = abspath(dirname(__file__))
dir_base = join(dir_scr, "..")
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

    master_host = f"{envs['MASTER_HOST']}:{envs['MASTER_PORT']}"
    if node == "slave":

        # デタッチ処理
        if fn.input_yn(f"\ndetach from master[ {master_host} ]. ok? (y/*) :"):
            print(f"\n---------- detach from [ {master_host} ] start")
            cmds = [
                f"{mysql_cmd} -e 'STOP SLAVE'",
                f"{mysql_cmd} -e 'RESET SLAVE'",
            ]
            for line in rp.cmdrun(_cmd=cmds, _encode="utf8"):
                sys.stdout.write(line)

    # リストア対象の指定
    dir_dump = abspath(join(dir_base, "vol", node, "dump"))
    print("\n----- dump directories list")
    for ref in os.listdir(dir_dump):
        if isdir(join(dir_dump, ref)):
            print(ref)
    print("\ninput restore target dump directry.")
    print("* place target \"yyyymmdd-hhiiss\" dump to \"vol/slave/dump\" in advance.:")
    _input = input("* enter as \"20210101-111111\". (empty to skip):")
    dir_dump_ref = f"{dir_dump}/{_input}"
    if _input != "":
        if not isdir(dir_dump_ref):
            print("[error] restore target none.")
            sys.exit()
        path_dump = f"/tmp/dump/{_input}/bin.dump"
        path_dump_ref = join(dir_dump_ref, "bin.dump")

        # リストア処理
        print(f"\n---------- restore to {container} start")
        cmds = [
            f"{mysql_cmd} -e 'SET PERSIST innodb_flush_log_at_trx_commit = 0'",
            f"{mysql_cmd} -e 'SET PERSIST sync_binlog = 0'",
        ]
        for line in rp.cmdrun(_cmd=cmds):
            sys.stdout.write(line)

        cmds = [f"{dk_cmd} bash -c 'mysql {envs['OPTROOT']} < {path_dump}'"]
        for line in rp.cmdrun(_cmd=cmds, _encode="utf8"):
            sys.stdout.write(line)

        cmds = [
            f"{mysql_cmd} -e 'SET PERSIST innodb_flush_log_at_trx_commit = 1'",
            f"{mysql_cmd} -e 'SET PERSIST sync_binlog = 1'",
        ]
        for line in rp.cmdrun(_cmd=cmds):
            sys.stdout.write(line)

        status_cmd = ""
        with open(join(dir_dump_ref, "status.txt")) as f:
            status_cmd = f.read()
        spl_status = status_cmd.split(" ")
        for st in spl_status:
            if "MASTER_LOG_FILE" in st:
                envs['REP_FILE'] = st.replace(",", "").replace("MASTER_LOG_FILE", "SOURCE_LOG_FILE")
            if "MASTER_LOG_POS" in st:
                envs['REP_POS'] = st.replace(",", "").replace("MASTER_LOG_POS", "SOURCE_LOG_POS")
        fn.setenv(envs, env_dst)
        print(f"\n---------- restore to {container} end")

    # アタッチ処理
    if node == "slave":

        if fn.input_yn(f"\nattach to master[ {master_host} ]. ok? (y/*) :"):
            print(f"\n---------- attach to [ {master_host} ] start")
            cmd = f"{mysql_cmd} -e \"\
CHANGE REPLICATION SOURCE TO \
{envs['REP_FILE']}, \
{envs['REP_POS']}, \
SOURCE_HOST='{envs['MASTER_HOST']}', \
SOURCE_PORT={envs['MASTER_PORT']}, \
SOURCE_USER='rep', \
SOURCE_PASSWORD='{envs['MYSQL_REP_PASSWORD']}';\
\""
            for line in rp.cmdrun(_cmd=[cmd], _encode="utf8"):
                sys.stdout.write(line)

            cmds = [
                f"{dk_cmd} bash -c \"mysql {envs['OPTROOT']} -e 'START SLAVE;'\"",
            ]
            for line in rp.cmdrun(_cmd=cmds, _encode="utf8"):
                sys.stdout.write(line)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='set env params')
    parser.add_argument('--node', '-n', help="(option) if not set dump_path, dump generate from node container. 'master' or 'slave'")
    args = parser.parse_args()

    if not args.node is None:
        if not args.node in ["master", "slave"]:
            print("[info] args error.")

    print("[info] initialize start.")
    main(args)
    print("[info] initialize end.")
