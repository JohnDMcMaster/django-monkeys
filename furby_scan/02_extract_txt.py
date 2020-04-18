import subprocess

for page in range(297):
    page += 1
    # print(page)
    # goes in object order, not text orientation
    # subprocess.check_call("pdf2text page/%04u.pdf >txt/%04u.txt" % (page, page), shell=True)
    subprocess.check_call("pdftotext -layout page/%04u.pdf txt/%04u.txt" % (page, page), shell=True)

