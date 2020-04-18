from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from typer.models import Die, Pdf, SiteSettings
from .forms import ContactForm


def homeView(request):
    """
    This view simply displays the list of all Dies in the database.
    These can be clicked on to enter data, instructions can be read,
    or administrators can inspect results.
    """
    # unsupported operand type(s) for +: 'QuerySet' and 'QuerySet'
    # taskList = Die.objects.all() + Pdf.objects.all()
    taskList = Pdf.objects.all()
    siteSettings = SiteSettings.objects.all()
    if len(siteSettings):
        siteSettings = siteSettings[0]
    introText = siteSettings.introText if siteSettings else ""

    context = {
                  'taskList': taskList,
                  'introText': introText
              }
    return render(request, 'home.html', context)


def contactView(request):
    """
    A simple view that shows the Contact form and sends an e-mail to the
    administrators when submitted.
    """
    submitSuccess = False
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            fromEmail = form.cleaned_data['fromEmail']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            finalMessage  = "From user : " + str(request.user.username) + "\n"
            finalMessage += "Return e-mail : " + str(fromEmail) + "\n\n"
            finalMessage += ("-" * 30) + "\n\n"
            finalMessage += message

            # Send the mail
            try:
                send_mail(subject, finalMessage, fromEmail, settings.EMAIL_CONTACT_LIST)
            except BadHeaderError:
                return HttpResponse('Invalid e-mail header found.')
            submitSuccess = True

    context = {
                  'form' : form,
                  'submitSuccess' : submitSuccess
              }
    return render(request, 'contact.html', context)


def profileView(request):
    """
    A view that lets the user edit their profile settings.
    """
    errorMessage = ""

    # Set the new e-mail address if a post is requested
    if request.method == 'POST':
        newEmail = request.POST['EmailField']
        try:
            validate_email(newEmail)
            request.user.email = newEmail
            request.user.save()
        except ValidationError:
            errorMessage = "Please enter a valid e-mail address"

    print(errorMessage)

    context = {
                  'error': errorMessage,
              }
    return render(request, 'profile.html', context)
