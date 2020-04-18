import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")

import django
django.setup()

from typer.models import Die, DieImage, TypedDie

Die.objects.all().delete()
DieImage.objects.all().delete()
TypedDie.objects.all().delete()


from typer.models import Pdf, PdfImage, TypedPdf

Pdf.objects.all().delete()
PdfImage.objects.all().delete()
TypedPdf.objects.all().delete()

