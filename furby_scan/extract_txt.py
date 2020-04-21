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

    parser = argparse.ArgumentParser(description="Dump furby .txt")
    add_bool_arg(parser, "--verbose", default=False)
    parser.add_argument("--salt", default=None)
    args = parser.parse_args()
    
    if args.salt:
        salt = args.salt
        print("salt: %s" % salt)

    pathlib.Path(txt_root_dir).mkdir(parents=True, exist_ok=True)
    freqs = {}
    for page in range(pages):
        page += 1
        freqs[page] = 0
        # os.mkdir(os.path.join(txt_root_dir, "%04u" % page))
        pathlib.Path(os.path.join(txt_root_dir, "%04u" % page)).mkdir(parents=True, exist_ok=True)

    print('Querying...')
    tpis = 297 * 5
    for tpi, tp in enumerate(TypedPdf.objects.all()):
        if tpi % 100 == 0:
            print("Check %u / %u" % (tpi + 1, tpis))
        if not tp.submitter:
            continue
        
        if tp.taskImage.task.name != 'furby_scan':
            continue
        typed = str(tp.typedField)
        page = int(tp.taskImage.page)
        # user should not be allowed to submit more than one per page
        basename = user2str(str(tp.submitter)) + ".txt"
        fn = os.path.join(txt_root_dir, "%04u" % page, basename)
        open(fn, "w").write(typed)
        freqs[page] += 1

    sol_min = min(freqs.values())
    sol_max = max(freqs.values())
    print("Pages: %u" % pages)
    print("Submissions: %u" % sum(freqs.values()))
    zero_solutions = sum([1 if x == 0 else 0 for x in freqs.values()])
    nonzero_solutions = sum([1 if x > 0 else 0 for x in freqs.values()])
    print("Covered: %u" % nonzero_solutions)
    print("0 solutions: %u" % zero_solutions)
    print("Min solutions: %u" % sol_min)
    print("Max solutions: %u" % sol_max)


main()

