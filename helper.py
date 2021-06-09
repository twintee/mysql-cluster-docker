import os
from os.path import join, dirname, isfile, isdir, abspath
import sys
import shutil
import json
import random, string
import socket
import shutil
import subprocess
from datetime import datetime as dt

def randstr(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def local_ip():
   return [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

def input_y(_txt, _abort=False):
    _input = input(_txt).lower()
    if _abort:
        if not _input in ["y", "yes"]:
            sys.exit()

def input_yn(_txt):
    _input = input(_txt).lower()
    if _input in ["y", "yes"]:
        return True
    return False

def getenv(_ref):
    print(f"get env from : {abspath(_ref)}")
    ret = {}
    if isfile(_ref):
        with open(_ref) as f:
            for line in f:
                spl = str(line).split('=', 1)
                ret[spl[0]] = spl[1].replace("\n", "")
    return ret

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
    with open(_dist, "w", encoding="utf-8", newline="\n") as dist:
        json.dump(_settings, dist, indent=4, ensure_ascii=False)

def setparam(_params, _key, _default=""):
    preset = None
    if _key in _params:
        preset = _params[_key]
    if preset is None:
        preset = _default
    print(f"-----preset {_key}: [{preset}]")
    _params[_key] = input(f"input {_key} value (empty to use preset):")
    return _params

def setparams(_params, _keys):
    for _key in _keys:
        preset = ""
        if _key in _params:
            preset = _params[_key]
        print(f"""-----
    {_key} : [{preset}]""")
        vset = input(f"    input value. (empty to use preset):")
        if vset != "":
            _params[_key] = vset
    return _params

def setenv(_params, _dst):

    lines = ""
    for k, v in _params.items():
        if lines != "":
            lines += "\n"
        lines += f"{k}={v}"
    with open(_dst, mode='w', newline="\n") as f:
        f.write(lines)

def update_file(_params, _org, _fix, _dst=None):
    """
    text update by dict items

    Parameters
    -----
    _params : dict
        replace text dictionary
    _org : str
        original file path.
    _fix : str
        replace key fix str
    _dst : str
        output path
    """
    target = _org
    if not _dst is None:
        shutil.copyfile(_org, _dst)
        target = _dst
    # ファイル行読みしながらテキスト置き換え
    txt = ""
    with open(_org, 'r', encoding="utf8") as f:
        txt = f.read()
        for key, val in _params.items():
            txt = str.replace(txt, f"{_fix}{key}{_fix}", val)
    # ファイル名保存
    with open(target, mode="w", encoding="utf8", newline="\n") as f:
        f.write(txt)

def rmdir(_ref, _skip=False):
    if isdir(_ref):
        rm_ref = False
        if _skip:
            rm_ref = True
        else:
            _input = input(f"remove [{_ref}]. ok? (y/*) :").lower()
            if _input in ["y", "yes"]:
                rm_ref = True
        if rm_ref:
            # ボリューム削除
            print(f"[info] remove {_ref}.")
            shutil.rmtree(_ref)

def chownr(_ref, _owner=None, _group=None, _self=True):
    for root, dirs, files in os.walk(_ref):
        for d in dirs:
            shutil.chown(os.path.join(root, d), _owner, _group)
        for f in files:
            shutil.chown(os.path.join(root, f), _owner, _group)
    if _self:
        shutil.chown(_ref, _owner, _group)

def chmodr(_ref, _permission, _self=True):
    for root, dirs, files in os.walk(_ref):
        for d in dirs:
            os.chmod(os.path.join(root, d), _permission)
        for f in files:
            os.chmod(os.path.join(root, f), _permission)
    if _self:
        os.chmod(_ref, _permission)

def cmdlines(_cmd, _cwd="", _encode='cp932', _wait_enter=False):
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
    if isinstance(_cmd, list):
        for ref in _cmd:
            print(f"\n[info] command executed. [{ref}]")
            if _wait_enter:
                input("enter to execute cmd. ([ctrl + c] to cancel script)")
            cmd = ref.split()
            if _cwd == "":
                proc = subprocess.Popen(cmd
                                        , stdout=subprocess.PIPE
                                        , stderr=subprocess.STDOUT
                                        , shell=True)
            else:
                proc = subprocess.Popen(cmd
                                        , cwd=_cwd
                                        , stdout=subprocess.PIPE
                                        , stderr=subprocess.STDOUT
                                        , shell=True)
            while True:
                line = proc.stdout.readline()
                if line:
                    yield line.decode(_encode)
                if not line and proc.poll() is not None:
                    break
    else:
        print(f"\n[info] command executed. [{_cmd}]")
        if _wait_enter:
            input("enter to execute cmd. ([ctrl + c] to cancel script)")
        cmd = _cmd.split()
        if _cwd == "":
            proc = subprocess.Popen(cmd
                                    , stdout=subprocess.PIPE
                                    , stderr=subprocess.STDOUT)
        else:
            proc = subprocess.Popen(cmd
                                    , cwd=_cwd
                                    , stdout=subprocess.PIPE
                                    , stderr=subprocess.STDOUT)
        while True:
            line = proc.stdout.readline()
            if line:
                yield line.decode(_encode)
            if not line and proc.poll() is not None:
                break

def info(message, time=True):
    print_message(message, time=time)

def error(message, time=True):
    print_message(message, error=True, time=time)

def print_message(message, error=False, time=True):
    """
    メッセージ表示
    """
    text = "[info]"
    if error:
        text = "[error]"
    if time:
        text += f" {dt.now().strftime('%Y-%m-%d %H:%M:%S')}"
    text += f" - {message}"
    print(f"{text}")
