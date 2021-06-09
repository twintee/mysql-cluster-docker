import os
from os.path import join, dirname, isfile, isdir, abspath
import sys
import datetime
import zipfile
import json
import subprocess

def getjson(_ref: str):
    """
    read json file

    Parameters
    ----------
    _ref : str
        open json file path
    """

    with open(_ref, 'r', encoding="utf-8") as f:
        return json.load(f)

def setjson(_dist: str, _settings):
    """
    save json file

    Parameters
    ----------
    _dist : str
        save json file path
    _settings : dict
        save target dict
    """
    with open(_dist, "w", encoding="utf-8") as dist:
        json.dump(_settings, dist, indent=4, ensure_ascii=False)

def cmdrun(_cmd:list, _cwd="", _encode='cp932'):
    """
    execute command and stream text

    Parameters
    -----
    _cmd : list or str
        commands list
    _cwd : str
        current work dir.
    _encode : str
        default value cp932 (set utf-8 fix errors)
    """
    for ref in _cmd:
        print(f"\n[info] command executed. [{ref}]")
        if _cwd == "":
            proc = subprocess.run(_cmd, shell=True
                        , stdout=subprocess.PIPE
                        , stderr=subprocess.STDOUT)
        else:
            proc = subprocess.run(_cmd, shell=True
                        , cwd=_cwd
                        , stdout=subprocess.PIPE
                        , stderr=subprocess.STDOUT)
        for line in proc.stdout.splitlines():
            if line:
                yield f"{line.decode(_encode)}\n"

def getdump_docker(_container, _dir_dump, _mysql_auth, _database, _compress=None):
    """
    get docker container mysql dump
    """

    print(f"[info] get {_container} mysqldump.")
    dk_cmd = f"docker exec -it {_container}"
    mysql_cmd = f"{dk_cmd} mysql {_mysql_auth}"
    dump_cmd = f"{dk_cmd} mysqldump {_mysql_auth}"

    # mysql テーブルロック
    print("\n---------- lock table")
    for line in cmdrun(_cmd=[f"{mysql_cmd} -e 'flush tables with read lock'"]):
        sys.stdout.write(line)

    ret = None
    print("\n---------- get dump data")
    stmp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    dir_tmp = join(_dir_dump, stmp)
    if not isdir(dir_tmp):
        print(f"[info] makedirs. :{dir_tmp}")
        os.makedirs(dir_tmp)
    path_dump = join(dir_tmp, f"bin.dump")
    # mysqldump
    db_opt = f"--databases {_database}"
    if _database == "all":
        db_opt = f"--all-databases"
    dump_cmd = f"{dk_cmd} /bin/bash -c \
\"\
mysqldump {_mysql_auth} \
--quote-names \
{db_opt} \
--master-data=2 \
--single-transaction \
--flush-logs \
--events > /tmp/dump/{stmp}/bin.dump\
\""
    for line in cmdrun(_cmd=[dump_cmd]):
        sys.stdout.write(line)

    # change master
    path_status = join(dir_tmp, f"status.txt")
    cnt = 0
    with open(path_dump) as fdump:
        for line in fdump:
            cnt += 1
            if 'CHANGE MASTER TO' in line:
                with open(path_status, mode="w", encoding="utf8") as f:
                    f.write(str(line).replace("-- ", "").replace("\n", "").replace(";", ""))
                break
            if cnt > 100:
                print("[error] replication log status is none.")
                sys.exit()

    if _compress:
        zip_dst = join(_dir_dump, f"{stmp}.zip")
        with zipfile.ZipFile(zip_dst, 'w', compression=zipfile.ZIP_DEFLATED) as fzip:
            fzip.write(path_status, arcname=f'{stmp}/status.json')
            fzip.write(path_dump, arcname=f'{stmp}/bin.dump')
    ret = dir_tmp

    # mysql ロック開放
    print("\n---------- unlock table")
    for line in cmdrun(_cmd=[f"{mysql_cmd} -e 'unlock tables;'"]):
        sys.stdout.write(line)

    return ret