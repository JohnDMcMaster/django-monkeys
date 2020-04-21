"""
Algorithm
Default to the .txt
Compare each submission to the default
Keep the one with the fewest "diff -w" lines


TODO:
-combine github results
-majority vote lines
"""


import sys
import os
import datetime
import hashlib
import binascii
import errno    
import os
import pathlib
import argparse
import glob
import subprocess


def add_bool_arg(parser, yes_arg, default=False, **kwargs):
    dashed = yes_arg.replace('--', '')
    dest = dashed.replace('-', '_')
    parser.add_argument(yes_arg,
                        dest=dest,
                        action='store_true',
                        default=default,
                        **kwargs)
    parser.add_argument('--no-' + dashed,
                        dest=dest,
                        action='store_false',
                        **kwargs)

def tobytes(buff):
    if type(buff) is str:
        #return bytearray(buff, 'ascii')
        return bytearray([ord(c) for c in buff])
    elif type(buff) is bytearray or type(buff) is bytes:
        return buff
    else:
        assert 0, type(buff)


def tostr(buff):
    if type(buff) is str:
        return buff
    elif type(buff) is bytearray or type(buff) is bytes:
        return ''.join([chr(b) for b in buff])
    else:
        assert 0, type(buff)

def defk(m, k, default):
    if not k in m:
        m[k] = default

def addk(m, k):
    m[k] = m.get(k, 0) + 1

def user2str(user):
    if salt:
        return hashlib.md5(tobytes(salt + user)).digest().hex()[0:8]
    return user

def main():
    verbose = True

    parser = argparse.ArgumentParser(description="Process files into best .txt guess")
    add_bool_arg(parser, "--verbose", default=False)
    parser.add_argument("--github-dir", default="furby_scan/github_txt")
    parser.add_argument("--ocr-dir", default="furby_scan/txt")
    parser.add_argument("--monkey-dir", default="furby_scan/txt_out")
    parser.add_argument("--out-dir", default="furby_scan/txt_best")
    args = parser.parse_args()
    
    pages = 297
    # TODO: combine github results
    github_dir_in = args.github_dir
    ocr_dir_in = args.ocr_dir
    monkey_dir_in = args.monkey_dir
    out_dir = args.out_dir


    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    for page in range(1, pages + 1):
        master_fn = os.path.join(ocr_dir_in, "%04u.txt" % page)
        source_fns = glob.glob(monkey_dir_in + "/%04u/*.txt" % page)
        diffs = {}
        for source_fn in source_fns:
            d = subprocess.check_output("diff -w %s %s || true" % (master_fn, source_fn), shell=True)
            d = tostr(d)
            ndiffs = len(d.split("\n"))
            diffs[ndiffs] = source_fn
        if len(diffs) == 0:
            verbose and print("pg %04u: use default" % page)
            txt = open(master_fn, "r").read()
        else:
            most_diffs, most_fn = sorted(diffs.items())[-1]
            verbose and print("pg %04u: %u diffs @ %s, %s" % (page, most_diffs, most_fn, list(diffs.keys())))
            txt = open(most_fn, "r").read()
        out_fn = os.path.join(out_dir, "%04u.txt" % page)
        open(out_fn, "w").write(txt)

main()

