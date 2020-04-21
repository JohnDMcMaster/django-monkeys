import subprocess

# sudo snap install pdftk

for page in range(297):
    page += 1
    print(page)
    subprocess.check_call("pdftk furbysource.pdf cat %u output page/%04u.pdf" % (page, page), shell=True)
    # subprocess.check_call("pdftk furbysource_text.pdf cat %u output page_pdf-txt/%04u.pdf" % (page, page), shell=True)

