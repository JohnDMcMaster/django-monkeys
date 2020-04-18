import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")

import django
django.setup()

from typer.models import Pdf, PdfImage, TypedPdf

# Add the die
pdf = Pdf(name="furby1")
pdf.save()

# Add its instructions (with custom [[[IMAGE_NAME (WIDTH HEIGHT)]]] markup)
pdf.instructions = """
    FIXME
    <br />
    Still have questions or suggestions?
    Try the contact form at the top of the page.
    We'll get back to you as soon as we are able.
    """
pdf.save()

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
    pi = PdfImage(task=pdf, page=page, image=imageName, seed=seed)
    pi.save()
    #print(dir(pi))

    # Add the empty typing fields to this new die image
    for i in range(5):
        td = pi.typedpdf_set.create(taskImage=pi)

