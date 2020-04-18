import subprocess

for page in range(297):
    page += 1
    print(page)
    subprocess.check_call("pdftoppm -png page/%04u.pdf > png/%04u.png" % (page, page), shell=True)


