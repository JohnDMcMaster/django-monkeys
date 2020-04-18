from django.db import models


class SiteSettings(models.Model):
    """
    A collection of settings that can be defined site-wide.
    """
    introText = models.TextField('Intro Text', blank=True)

    def __str__(self):
        return ("Site settings:\nintroText:%s" % (self.introText))

#############################################################################
# Die
#############################################################################

# Task
class Die(models.Model):
    """
    A model storing information for a die that has been imaged.
    """
    name = models.CharField(max_length=256)
    instructions = models.TextField('Instructions', blank=True)

    def __str__(self):
        return ("%s" % (self.name))


# TaskInstructonsImage
class DieInstructionsImage(models.Model):
    """
    A class to hold an instruction image for the Die class' instructions.
    """
    task = models.ForeignKey(Die, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    image = models.ImageField('Die Image')

    def __str__(self):
        return ("Instructions image %s for Die %s" % (self.name, self.task.name))

# TaskImage
class DieImage(models.Model):
    """
    One of the individual images associated with a referenced chip die.
    """
    task = models.ForeignKey(Die, on_delete=models.CASCADE)
    cropRow = models.IntegerField('Cropped Row')
    cropCol = models.IntegerField('Cropped Column')
    image = models.ImageField('Die Image')

    # These two are specific to images of ROMs
    # It's possible this should live in a subclass of DieImage someday
    bitWidth = models.IntegerField('Bits wide', default=0)
    bitHeight = models.IntegerField('Bits tall', default=0)

    def __str__(self):
        return ("%s_%02d_%02d" % (self.die.name, self.cropCol, self.cropRow))

# TypedTask
class TypedDie(models.Model):
    """
    Contains typed text for a given die image.
    References back to the Die Image it's associated with.
    """
    taskImage = models.ForeignKey(DieImage, on_delete=models.CASCADE)
    submitter = models.ForeignKey('auth.User', null=True, blank=True)
    typedField = models.TextField('Typed Info', blank=True)
    submitDate = models.DateTimeField('Time Submitted', null=True, blank=True)

    def completed(self):
        """
        """
        return (self.typedField != "")

    def __str__(self):
        return ('TypedDie for DieImage "%s" (%r)' % (self.taskImage, self.completed()))

DieMap = {
    "Task": Die,
    "TaskInstructionsImage": DieInstructionsImage,
    "TaskImage": DieImage,
    "TypedTask": TypedDie,
}

#############################################################################
# Pdf
#############################################################################

# Task
class Pdf(models.Model):
    """
    A model storing information for a pdf that has been imaged.
    """
    name = models.CharField(max_length=256)
    instructions = models.TextField('Instructions', blank=True)

    def __str__(self):
        return ("%s" % (self.name))

# TaskInstructonsImage
class PdfInstructionsImage(models.Model):
    """
    A class to hold an instruction image for the Die class' instructions.
    """
    task = models.ForeignKey(Pdf, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    image = models.ImageField('Pdf Image')

    def __str__(self):
        return ("Instructions image %s for Task %s" % (self.name, self.task.name))

# TaskImage
class PdfImage(models.Model):
    """
    One of the individual images associated with a referenced pdf.
    """
    task = models.ForeignKey(Pdf, on_delete=models.CASCADE)
    page = models.IntegerField('Page number')
    image = models.ImageField('Pdf Image')
    seed = models.TextField()

    def __str__(self):
        return ("%s_%04u" % (self.task.name, self.page))

# TypedTask
class TypedPdf(models.Model):
    """
    Contains typed text for a given pdf image.
    References back to the Pdf Image it's associated with.
    """
    taskImage = models.ForeignKey(PdfImage, on_delete=models.CASCADE)
    submitter = models.ForeignKey('auth.User', null=True, blank=True)
    typedField = models.TextField('Typed Info', blank=True)
    submitDate = models.DateTimeField('Time Submitted', null=True, blank=True)

    def completed(self):
        """
        """
        return (self.typedField != "")

    def __str__(self):
        return ('TypedPdf for PdfImage "%s" (%r)' % (self.taskImage, self.completed()))

PdfMap = {
    "Task": Pdf,
    "TaskInstructionsImage": PdfInstructionsImage,
    "TaskImage": PdfImage,
    "TypedTask": TypedPdf,
}

TaskMap = {
    Die: DieMap,
    Pdf: PdfMap,
}

