import subprocess

txt = ""

# for page in range(297):
for page in range(10):
    page += 1
    txt += open("txt/%03u.txt" % page, "r").read()

open("final.txt", "w").write(txt)

