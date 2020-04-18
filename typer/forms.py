from django import forms
from .models import TypedDie, TypedPdf


class DieMonkeyTyperForm(forms.ModelForm):
    """
    This form displays a TypedPdf object and validates information typed
    by a user.
    """

    def __init__(self, *args, **kwargs):
        """
        Standard initialization routine, but with an explicit definition of
        the typedField's width and height based on database info.
        """
        super(DieMonkeyTyperForm, self).__init__(*args, **kwargs)
        self.fields['typedField'].widget = forms.Textarea(attrs={'cols': self.instance.dieImage.bitWidth+2,
                                                                 'rows': self.instance.dieImage.bitHeight+2})

    class Meta:
        model = TypedDie
        fields = ['typedField']


    def clean_typedField(self):
        """
        A validator for the typedField field that insures the field isn't blank,
        the data contains only valid characters, and various other fun things.
        """
        data = self.cleaned_data['typedField']

        # Remove whitespace from each line
        cleanedData = ""
        for line in data.splitlines():
            stripped = line.strip()
            if len(stripped) == 0:
                continue
            cleanedData += stripped
            cleanedData += "\n"

        # TODO: Settings in the Models for which validators to use

        # Validation 0 : Insure there is some data present
        if not len(cleanedData):
            raise forms.ValidationError('No data present')

        # Validation 1 : Insure the data is binary only
        okChars = '01?'
        for line in cleanedData.splitlines():
            allOk = all(c in okChars for c in line)
            if not allOk:
                raise forms.ValidationError('Invalid characters entered (just 0, 1, and ? please)')

        # Validation 2 : Insure the data is the proper number of bits in all dimensions
        colCount = 0
        rowCount = len(cleanedData.splitlines())
        bitWidth = self.instance.dieImage.bitWidth
        bitHeight = self.instance.dieImage.bitHeight
        if rowCount != bitHeight:
            raise forms.ValidationError('You gave me %d rows of typed bits but I need %d' % (rowCount, bitHeight))
        for linei, line in enumerate(cleanedData.splitlines()):
            lineLen = len(line.strip())
            if lineLen != bitWidth:
                raise forms.ValidationError('Row %d has %d bits but should have %d bits' % (linei + 1, lineLen, bitWidth))

        return cleanedData

class PdfMonkeyTyperForm(forms.ModelForm):
    """
    This form displays a TypedPdf object and validates information typed
    by a user.
    """

    def __init__(self, *args, **kwargs):
        """
        Standard initialization routine, but with an explicit definition of
        the typedField's width and height based on database info.
        """
        super(PdfMonkeyTyperForm, self).__init__(*args, **kwargs)
        self.fields['typedField'].widget = forms.Textarea(attrs={'cols': 80+2,
                                                                 'rows': 80})
        """
        print(type(self))
        print(self.initial)
        print(dir(self))
        # AttributeError: 'str' object has no attribute 'get'
        # self.initial = "stromboli"

        # <class 'django.forms.fields.CharField'>
        print(type(self.fields['typedField']))
        print(dir(self.fields['typedField']))
        # <class 'django.forms.widgets.Textarea'>
        print(type(self.fields['typedField'].widget))
        print(dir(self.fields['typedField'].widget))
        # <class 'NoneType'>
        print(type(self.fields['typedField'].initial))
        print(dir(self.fields['typedField'].initial))
        # https://stackoverflow.com/questions/37380627/how-do-you-add-default-value-to-django-form-textarea
        # hmm not working....                                              
        self.fields['typedField'].initial = 'This is default text.'
        """

    class Meta:
        model = TypedPdf
        fields = ['typedField']


    def clean_typedField(self):
        """
        A validator for the typedField field that insures the field isn't blank,
        the data contains only valid characters, and various other fun things.
        """
        data = self.cleaned_data['typedField']

        # Remove whitespace from each line
        cleanedData = ""
        for line in data.splitlines():
            stripped = line.strip()
            cleanedData += stripped
            cleanedData += "\n"

        # TODO: Settings in the Models for which validators to use

        # Validation 0 : Insure there is some data present
        if not len(cleanedData):
            raise forms.ValidationError('No data present')

        return cleanedData
