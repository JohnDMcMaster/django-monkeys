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
task.instructions = """
    Thank you for your interest in the sipr0n crowdsource project!
    We appreciate your time and want to make the most of it.
    Please review the below instructions to ensure we are able to use your results.<br />
    <br />
    What: these images are scans of the original Furby assembly source code.
    Unfortunately the scans are noisy and automatic image to text conversion is difficult.
    So we are looking for help correcting errors.
    <br />
    [[[weird]]]<br />
    <br />
    There are some odd character sequences in the print outs.
    These are caused by a character encoding issue in the print out.
    Please type them out literally, even if they look strange, as if they are verbatim we know how to fix them.
    <br />
    Still have questions or suggestions?
    Try the contact form at the top of the page.
    We'll get back to you as soon as we are able.
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

