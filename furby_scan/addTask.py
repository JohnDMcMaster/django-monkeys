import sys
sys.path.append(".") 

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")

import django
django.setup()

from typer.models import Pdf, PdfImage, TypedPdf
import glob

# Add the die
task = Pdf(name="furby1")
task.save()

# Add its instructions (with custom [[[IMAGE_NAME (WIDTH HEIGHT)]]] markup)
# Images created by zooming 200% into pdf
task.instructions = """
Thank you for your interest in the sipr0n crowdsource project! We appreciate your time and want to make the most of it. Please review the below instructions to ensure we are able to use your results.
<br />
<br />
[[[furby_scan_furby]]]
<br />
<br />
What: the Furby is an iconic talking toy from the late 90s.
A couple of years ago scans of the original Furby source code were acquired.
Unfortunately the scans are noisy and automatic image to text conversion is difficult.
So we're asking the community to help preserve game history by proofreading computer generated transcripts.
Generating a proper copy of the Furby source code will be enormously valuable to understanding how it works.
Let's get to it!
<br />
<br />
You will be presented with a scanned source code page at left and our best guess at the original text at right.
Please review for errors such as those outlined below.
<br />
<br />
First, due to various issues we are unable to split the pages into smaller tasks.
So the images are relatively large and this is best completed on systems with a large screen such as a laptop or a desktop.
So apologies if you only have mobile, but you may not be able to help with this specific project.
<br />
<br />
[[[furby_scan_weird1]]]
<br />
<br />
Sometimes large runs of odd looking characters like above appear due to a print out issue. Please type them out literally the best you can. For example, please type above as:
<br />
;EIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII
<br />
IIII>
<br />
;*   MODIFICATION LIST :
<br />
<br />
We will fix these formatting issues properly in post processing.
<br />
<br />
[[[furby_scan_weird2]]]
<br />
<br />
Another print out example. This should be typed as:
<br />
<br />
;UAAAAAAAAAAAAAAAAAAAAAAAAXAAAAAAAAAAAAAAAAAAAAAAAAA?
<br />
;' Variable definition      (Ram = $80 to $FF)
<br />
;AAAAAAAAAAAAAAAAAAAAAAAAAXAAAAAAAAAAAAAAAAAAAAAAAAAU
<br />
<br />
[[[furby_scan_wrap]]]
<br />
<br />
Some lines are wrapped.
Please type them verbatim as separate lines.
We will handle text wrapping in post processing.
<br />
<br />
[[[furby_scan_semicolon]]]
<br />
<br />
Please pay attention to semicolons. They are littered throughout the code, are very important, and are often incorrectly translated. Here you can see examples at the beginning of lines as well as towards the end of lines.
<br />
<br />
Don't worry too much about whitespace other than making sure there is at least one space where expected.
For example, if the above table doesn't line up, don't worry about it.
<br />
<br />
[[[furby_scan_source]]]
<br />
<br />
Finally, we are very interested in getting assembly directives correct.
These are anything before a ";" and are often in capital letters.
<br />
<br />
Still have questions or suggestions? Try the contact form at the top of the page.
We'll get back to you as soon as we are able.
Thanks again for your help!
    """


# And the images that go with the instructions
for fn in glob.glob("furby_scan/help/*.png"):
    basename = os.path.basename(fn)
    simplename = basename.split(".")[0]
    static_path = "furby_scan/help/%s" % basename
    task.pdfinstructionsimage_set.create(task=task, name=simplename, image=static_path)
    
task.save()

print("Adding images")
# Add the images to the die
for page in range(297):
    page += 1
    if page % 11 == 1:
        print("Page %u / %u" % (page, 297))
    # loaded later from static
    imageName = "furby_scan/%04u.png" % (page,)
    # loaded now directly into DB
    seed = open("furby_scan/txt/%04u.txt" % (page,), "r").read()
    pi = PdfImage(task=task, page=page, image=imageName, seed=seed)
    pi.save()
    #print(dir(pi))

    # Add the empty typing fields to this new die image
    for i in range(5):
        td = pi.typedpdf_set.create(taskImage=pi)

