#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from os.path import join, dirname, abspath, isfile, isdir
import subprocess as sp
import argparse

dir_scr = abspath(dirname(__file__))
dir_base = abspath(join(dir_scr, ".."))
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
    dir_dump = abspath(join(dir_base, "vol", node, "dump"))

    fn.input_y(f"start to get {container} dump. (y/*):")
    database = envs['MYSQL_DATABASE']
    if _args.all:
        database = "all"
    dump_path = rp.getdump_docker(container
            , dir_dump
            , f"{envs['OPTROOT']} -u root"
            , database
            , _args.compress)
    fn.chmodr(dump_path, 0o777)

    print(f"\n[info] generate dump file: [{dump_path}].")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='set env params')
    parser.add_argument('--node', '-n', help="(option) force node type 'master' or 'slave' or 'all'")
    parser.add_argument('--all', '-a', help="(option) all database dump", action="store_true")
    parser.add_argument('--compress', '-c', help="(option) compress dump files", action="store_true")
    args = parser.parse_args()

    if not args.node is None:
        if not args.node in ["master", "slave"]:
            print("[info] args error.")

    print("[info] get dump start.")
    main(args)
    print("[info] get dump end.")
