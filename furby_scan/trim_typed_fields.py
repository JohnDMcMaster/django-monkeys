import sys
sys.path.append(".") 

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")
import django
django.setup()
from typer.models import Pdf, PdfImage, TypedPdf
import datetime
import hashlib
import binascii
import errno    
import os
import pathlib
import argparse


pages = 297
salt = None
txt_root_dir = "furby_scan/txt_out"

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
    global salt

    parser = argparse.ArgumentParser(description="Reduce typed fields from 5 to 3")
    add_bool_arg(parser, "--verbose", default=False)
    add_bool_arg(parser, "--dry", default=True)
    args = parser.parse_args()

    want_submits = 3
    dry = args.dry
    verbose = args.verbose

    buckets = {}
    for page in range(pages):
        page += 1
        buckets[page] = []

    # Order may be random, so start by indexing everything
    # not a huge data set so should be fine I think
    print('Pass: index DB')
    tpis = 297 * 5
    for tpi, tp in enumerate(TypedPdf.objects.all()):
        if tpi % 200 == 0:
            print("Index typer %u / %u" % (tpi + 1, tpis))
        buckets[int(tp.taskImage.page)].append(tp)

    # pages may not be sorted, so don't confuse pagei and page
    deletes = 0
    fail_deletes = 0
    for pagei, (page, tps) in enumerate(sorted(buckets.items())):
        if pagei % 20 == 0:
            print("Check page %u / %u" % (pagei + 1, pages))

        have = len(tps)
        submits = sum([1 if tp.submitter else 0 for tp in tps])
        verbose and print("page %u: %u / %u submits" % (page, submits, have))
        n_delete = have - want_submits
        if n_delete <= 0:
            continue
        # Look for some entries to purge
        for tp in tps:
            if n_delete <= 0:
                break
            if not tp.submitter:
                verbose and print("DELETE: %s" % str(tp))
                deletes += 1
                if not dry:
                    tp.delete()
                n_delete -= 1
        if n_delete > 0:
            print("WARNING: was unable to find enough entries to delete")
            fail_deletes += n_delete

    print("Deletes: %u" % deletes)
    print("Unable to delete: %u" % fail_deletes)

main()

