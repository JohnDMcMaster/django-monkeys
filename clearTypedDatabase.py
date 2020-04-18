import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")

import django
django.setup()

from typer.models import Die, DieInstructionsImage, DieImage, TypedDie

Die.objects.all().delete()
# DieInstructionsImage.all().delete()
DieImage.objects.all().delete()
TypedDie.objects.all().delete()


from typer.models import Pdf, PdfInstructionsImage, PdfImage, TypedPdf

Pdf.objects.all().delete()
# PdfInstructionsImage.all().delete()
PdfImage.objects.all().delete()
TypedPdf.objects.all().delete()

