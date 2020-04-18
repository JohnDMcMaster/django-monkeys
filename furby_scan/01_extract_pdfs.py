import subprocess

for page in range(297):
    page += 1
    print(page)
    subprocess.check_call("pdftk furbysource.pdf cat %u output page/%04u.pdf" % (page, page), shell=True)

