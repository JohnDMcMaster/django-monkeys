import os
import re
import random
import logging
import time

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags import staticfiles
from .models import Die, DieImage, TypedDie
from .models import Pdf, PdfImage, TypedPdf
from .models import TaskMap
from .forms import DieMonkeyTyperForm, PdfMonkeyTyperForm

TyperFormMap = {
    Die: DieMonkeyTyperForm,
    Pdf: PdfMonkeyTyperForm,
}

Image2TypedTask = {
    DieImage: TypedDie,
    PdfImage: TypedPdf,
}

Task2TypedTask = {
    Die: TypedDie,
    Pdf: TypedPdf,
}

Task2TaskImage = {
    Die: DieImage,
    Pdf: PdfImage,
}

logger = logging.getLogger(__name__)

def getTaskByName(name):
    taskObject = Die.objects.filter(name=name)
    if len(taskObject) == 1:
        return taskObject[0]
    taskObject = Pdf.objects.filter(name=name)
    if len(taskObject) == 1:
        return taskObject[0]
    raise ValueError("can not find task %s" % name)

def getTypedTaskByName(taskId):
    typedObject = TypedDie.objects.filter(id=taskId)
    if len(typedObject) == 1:
        return typedObject[0]
    typedObject = TypedPdf.objects.filter(id=taskId)
    if len(typedObject) == 1:
        return typedObject[0]
    raise ValueError("can not find typed task %s" % name)

def getTypedTaskClassByName(taskId):
    typedObject = TypedDie.objects.filter(id=taskId)
    if len(typedObject) == 1:
        return TypedDie
    typedObject = TypedPdf.objects.filter(id=taskId)
    if len(typedObject) == 1:
        return TypedPdf
    raise ValueError("can not find typed task %s" % taskId)

def indexViewGET(request, taskName):
    tstart = time.time()
    # Standard page display
    taskObject = getTaskByName(taskName)
    TypedTask = Task2TypedTask[type(taskObject)]
    print("Finding tasks...")
    allAvailableFields = TypedTask.objects.filter(Q(typedField="") & Q(taskImage__task=taskObject))
    print("Tasks; %s" % len(allAvailableFields))

    thingsUserHasTyped = TypedTask.objects.filter(~Q(typedField="") & Q(submitter=request.user) & Q(taskImage__task=taskObject))
    setTyped = [td.taskImage_id for td in thingsUserHasTyped]
    usableFields = list(filter(lambda x: x.taskImage_id not in setTyped, allAvailableFields))
    #print 'avail', len(allAvailableFields)
    #print 'typed', len(setTyped)
    #print 'usable', len(usableFields)

    if not usableFields:
        return HttpResponse("<html><body>All fields have been typed for this task. Check back later to see if there are other tasks to type.</body></html>")

    """
    simple
    0.061 sec
    0.046 sec
    0.049 sec

    selTask()
    3 rolls
    0.066 sec
    0.113 sec
    0.086 sec

    noticible but acceptable
    QoR improvement is pretty good, so lets roll with it
    """
    def selTask():
        # Choose a random field to display
        # Try a few times and use the one with the lowest number of completions
        scores = {}
        for i in range(3):
            randomField = random.randint(0, len(usableFields)-1)
            randomId = usableFields[randomField].id
            typedTasks = TypedTask.objects.filter(Q(taskImage=usableFields[randomField].taskImage))
            score = sum([1 if task.typedField else 0 for task in typedTasks])
            # No coverage?
            if score == 0:
                print("selTask %u found 0" % len(scores))
                return randomId
            scores[score] = randomId
        print("selTask scores", scores)
        # Take something tied for lowest number of completions
        _completions, randomId = sorted(scores.items())[0]
        return randomId

    randomId = selTask()


    tend = time.time()
    print("%0.3f sec" % (tend - tstart,))

    # Display the random page
    return imageInput(TypedTask, request, randomId, seed=True)


def indexViewPOST(request, dieName):
    # Data has been POSTed
    # Pull the previous die field out of the form's hidden data
    dieId = int(request.POST['taskField'])

    taskField = getTypedTaskByName(dieId)
    TypedTask = type(taskField)

    someoneCompletedTheFieldBeforeYou = taskField.completed()

    # Create a form object from the post data and knowledge of which taskField we're dealing with
    form = PdfMonkeyTyperForm(request.POST, instance=taskField)

    # Insure input is valid (if it is, data is stored in taskField, but not saved to the database)
    # TODO: There is a very good chance exceptions aren't being used correctly here
    if not form.is_valid():
        # Redisplay the same page but with an error message
        error = form.errors.as_data()['typedField'][0].message
        return imageInput(TypedTask, request, taskField.id, error, form.data['typedField'])

    # If the strange situation occurred where someone snuck in and completed the field before you
    if someoneCompletedTheFieldBeforeYou:
        # TODO: Convert to django/Python logging
        dieObject = taskField.taskImage.die
        taskImageObject = taskField.taskImage
        print("User %s attempted to submit %s die image %s typed id %d, but someone else did first" %
              (request.user,
               dieObject,
               taskImageObject,
               dieId))

        # Find the next available taskField that is not completed
        availableFields = TypedTask.objects.filter(Q(typedField="") & Q(taskImage__task=dieObject) & Q(taskImage=taskImageObject))

        # If there is no place to squeeze the data in, just return the next random page
        if not len(availableFields):
            print("And there was no place free to put their work, so it got trashed")
            return HttpResponseRedirect('/typer/' + dieName)

        # If there is space, stuff it in the first object that's available
        print("So we are adding it to field %s instead" % taskField)
        taskField = availableFields[0]

    # Submit the user's input
    taskField.submitter = request.user
    taskField.submitDate = timezone.now()
    # No need to update typedField since it's already saved in the is_valid() function call above
    taskField.save()

    # Return the next random page
    return HttpResponseRedirect(reverse('typer:index', kwargs={'dieName':dieName}))

def indexView(request, dieName):
    """
    This view displays a randomly choosen DieImage for a given Die.  Secret
    data about which die has been randomly chosen passes through to the POST
    method since this view decides it dynamically.

    Note:
    allAvailableFields = allAvailableFields.exclude(Q(taskImage=tuht.taskImage))
    Resulted in large AND NOT query after adding many entries
    Instead two separate queries and subtract out manually
    """
    # userIsStaff = request.user.is_staff

    if request.method == 'GET':
        return indexViewGET(request, dieName)
    else:
        return indexViewPOST(request, dieName)

def imageInput(TypedTask, request, fieldId, error=None, seed=False, fieldData=None):
    """
    Helper function for the indexView - responsible for creating the page
    that features the input interface & possible error messages.
    """
    # Recover the requested die image and its corresponding die
    taskField = get_object_or_404(TypedTask, id=fieldId)
    di = taskField.taskImage
    d = di.task

    if seed:
        fieldData = di.seed

    # Populate the form with the raw data from the previous submit if there was an error
    """
    if error and fieldData:
        form = PdfMonkeyTyperForm(instance=taskField, initial={'typedField': fieldData})
    else:
        form = PdfMonkeyTyperForm(instance=taskField, initial={'typedField': fieldData})
    """
    # think this can be simplified?
    form = PdfMonkeyTyperForm(instance=taskField, initial={'typedField': fieldData})

    # Prune off just the filename from the taskImage url
    taskImageBasename = os.path.basename(taskField.taskImage.image.url)

    # Display the input page
    context = {
                  'task': d,
                  'taskImage': di,
                  'taskImageBasename': taskImageBasename,
                  'typedTask': taskField,
                  'form' : form,
                  'error' : error,
              }
    # FIXME: handle
    # return render(request, 'typer/imageInput.html', context)
    return render(request, 'typer/pdfInput.html', context)


def taskSpecificUserStatisticsView(request, dieName, userName):
    """
    A view that shows interesting statistics for the user specified in the url.
    """

    # If the given username isn't the logged-in user, see if it's staff.  If not, go no further.
    if userName != request.user.username and not request.user.is_staff:
        return HttpResponse("<html><body>Only administrators can access user statistics directly</body></html>")

    # Get the User object from the username
    dieObject = getTaskByName(dieName)
    TypedTask = Task2TypedTask[type(dieObject)]
    TaskImage = Task2TaskImage[type(dieObject)]
    specifiedUser = None
    for user in User.objects.all():
        if userName == user.username:
            specifiedUser = user
    if specifiedUser is None:
        return HttpResponse("<html><body>The user %s does not exist.</body></html>" % userName)

    # Carry on
    # typer.models.Pdf
    print(type(dieObject))
    # typer.models.TypedPdf
    print(TypedTask)
    userTypedTheseFields = TypedTask.objects.filter(Q(taskImage__task=dieObject) & Q(submitter=specifiedUser))

    # How does this user's entry count compare to the others?
    userEntryTupleList = list()
    for user in User.objects.all():
        if user == specifiedUser:
            continue
        otherUserTypedFields = TypedTask.objects.filter(Q(taskImage__task=dieObject) & Q(submitter=user))
        userEntryTupleList.append((user, len(otherUserTypedFields)))
    sortedByEntry = [x for (y,x) in sorted(userEntryTupleList, key=lambda pair: pair[1], reverse=True)]
    quantityRank = len(sortedByEntry)
    for i in range(len(sortedByEntry)):
        if len(userTypedTheseFields) > sortedByEntry[i]:
            quantityRank = i
            break
    quantityRank += 1

    # For each field the user typed, compare against other users' results
    comparisonMessages = list()
    for userTypedField in userTypedTheseFields:
        typedFieldCount = 0
        perfectMatchCount = 0
        allFieldsRelatedToUserTypedField = TypedTask.objects.filter(Q(taskImage=userTypedField.taskImage) & ~Q(submitter=specifiedUser))
        for field in allFieldsRelatedToUserTypedField:
            if field.completed():
                perfectMatchCount += 1 if (userTypedField.typedField == field.typedField) else 0
                typedFieldCount += 1
        # Construct a interesting message
        if typedFieldCount > 0:
            if perfectMatchCount == typedFieldCount:
                comparisonMessages.append("Your data matches the data everyone else typed for this image")
            elif perfectMatchCount != typedFieldCount:
                matchPercent = (float(perfectMatchCount) / float(typedFieldCount)) * 100.0
                comparisonMessages.append("Your data conflicts with what others typed.\nYou agree with %.0f%% of the others." % (matchPercent))
        else:
            comparisonMessages.append("You are the only one to type data for this image so far")

    # TODO: Low importance fix - if you're an admin and you 'typed the same image twice' this number is wrong
    allImagesForDie = TaskImage.objects.filter(Q(task=dieObject))
    typedPercent = round(float(len(userTypedTheseFields)) / float(len(allImagesForDie)) * 100.0, 2)
    context = {
                  'die' : dieObject,
                  'typedCount' : len(userTypedTheseFields),
                  'typedPercent' : typedPercent,
                  'quantityRank' : quantityRank,
                  'specifiedUser' : specifiedUser,
                  'fieldsAndMessages' : zip(userTypedTheseFields, comparisonMessages)
              }
    html = {
        Die: 'typer/userStatisticsDie.html',
        Pdf: 'typer/userStatisticsPdf.html',
    }[type(dieObject)]
    return render(request, html, context)


def taskInstructionsView(request, dieName):
    """
    A view that simply displays the instructions image and instruction text
    for the given Die.
    """
    
    taskObject = getTaskByName(dieName)
    instructions = taskObject.instructions

    # Find all the instances of images in our special markup [[[IMAGE_NAME (WIDTH HEIGHT)]]]
    m = re.finditer(r'\[\[\[(.*?)\]\]\]', instructions)
    for foundMatch in m:
        noBrackets = foundMatch.group(0).replace("[", "").replace("]", "")
        splitData = noBrackets.split()
        imageName = splitData[0]
        if len(splitData) > 1:
            imageWidth = int(splitData[1])
            imageHeight = int(splitData[2])
        if type(taskObject) == Die:
            imageObject = taskObject.dieinstructionsimage_set.filter(Q(name=imageName))
        elif type(taskObject) == Pdf:
            imageObject = taskObject.pdfinstructionsimage_set.filter(Q(name=imageName))
        else:
            assert 0
        imageUrl = staticfiles.static(imageObject[0].image.url)
        if len(splitData) > 1:
            refText = """<img src="%s" width=%d height=%d>""" % (imageUrl, imageWidth, imageHeight)
        else:
            refText = """<img src="%s">""" % (imageUrl)
        instructions = instructions.replace(foundMatch.group(0), refText)

    # Copy the instructions back to a local die object (no database write)
    taskObject.instructions = instructions
    context = {
                  'die' : taskObject
              }
    return render(request, 'typer/instructions.html', context)


def adminStatisticsView(request, dieName):
    """
    """
    dieObject = getTaskByName(dieName)
    TypedTask = Task2TypedTask[type(dieObject)]

    # Get how many fields and how many have been typed
    allFields = TypedTask.objects.filter(Q(taskImage__task=dieObject))
    typedFields = TypedTask.objects.filter(Q(taskImage__task=dieObject) & ~Q(typedField=""))

    # Get a list of who's on first
    scoreboard = list()
    for user in User.objects.all():
        userTyped = TypedTask.objects.filter(~Q(typedField="") & Q(submitter=user) & Q(taskImage__task=dieObject))
        scoreboard.append( (user, len(userTyped)) )
    sortedScores = sorted(scoreboard, key=lambda tup: tup[1], reverse=True)

    context = {
                  'die' : dieObject,
                  'allFieldCount' : len(allFields),
                  'allTypedCount' : len(typedFields),
                  'scoreboard' : sortedScores
              }
    return render(request, 'typer/adminStatistics.html', context)


def adminSummaryHomeView(request, dieName):
    """
    An administrative view that displays a list of images and info about
    the typed information for each for the given Die.  The administrator
    can see how much data has been entered for each image and click on
    the image to open a new view showing more details.
    """
    dieObject = getTaskByName(dieName)
    TypedTask = Task2TypedTask[type(dieObject)]
    TaskImage = Task2TaskImage[type(dieObject)]
    allAvailableDieImages = TaskImage.objects.filter(Q(task=dieObject))
    allApplicableTypedDies = TypedTask.objects.filter(Q(taskImage__task=dieObject))

    # Count all the entered fields for this die image (TODO: There must be a more Pythonic way to do this)
    totalFields = 0
    totalCompletedFields = 0
    dieIsCompleted = list()
    taskImageEntryCounts = list()
    # TODO: This is very slow right now - seems to be 2/3 python and 1/3 html - could be sped up with a Paginator
    for di in allAvailableDieImages:
        typedFields = allApplicableTypedDies.filter(Q(taskImage=di))
        completedFieldCount = 0
        for tf in typedFields:
            if tf.completed():
                completedFieldCount += 1
        totalFields += len(typedFields)
        totalCompletedFields += completedFieldCount
        taskImageEntryCounts.append(completedFieldCount)
        dieIsCompleted.append(completedFieldCount == len(typedFields))

    completedPercent = round(float(totalCompletedFields) / float(totalFields) * 100.0, 2)

    context = {
                  'die': dieObject,
                  'dieImageInfo': zip(allAvailableDieImages, taskImageEntryCounts, dieIsCompleted),
                  'completedPercent': completedPercent
              }
    return render(request, 'typer/adminSummaryHome.html', context)


def adminSummaryView(request, dieName, imageId):
    """
    This administrative view displays a summary of all the entered information
    for a given Die and DieImage.  One can also do rudimentary changes to the
    entered data and compare results.
    """
    dieObject = getTaskByName(dieName)
    TypedTask = Task2TypedTask[type(dieObject)]
    TaskImage = Task2TaskImage[type(dieObject)]
    taskImage = TaskImage.objects.filter(id=imageId)[0]
    allAvailableFields = TypedTask.objects.filter(Q(taskImage__task=dieObject) & Q(taskImage__id=imageId))

    if request.method == "POST":
        # Pull which clear button was pressed
        clearButtonsPressed = [k for k,v in request.POST.items() if k.startswith('clearButton')]
        if len(clearButtonsPressed) > 0:
            firstClearButtonPressed = clearButtonsPressed[0]
            clearNumberRe = re.search(r'(\d+)$', firstClearButtonPressed)
            clearNumber = int(clearNumberRe.group(0))
            workingField = allAvailableFields[clearNumber]

            # Clear the form
            workingField.submitter = None
            workingField.submitDate = None
            workingField.typedField = ""
            workingField.save()
            allAvailableFields[clearNumber].refresh_from_db()

        # Pull which save button was pressed
        saveButtonsPressed = [k for k,v in request.POST.items() if k.startswith('saveButton')]
        if len(saveButtonsPressed) > 0:
            firstSaveButtonPressed = saveButtonsPressed[0]
            saveNumberRe = re.search(r'(\d+)$', firstSaveButtonPressed)
            saveNumber = int(saveNumberRe.group(0))
            workingField = allAvailableFields[saveNumber]

            form = PdfMonkeyTyperForm(request.POST, instance=workingField)
            if not form.is_valid():
                # TODO: Do something interesting here (really the admin should know better).
                #       As for now, it just reverts your changes.
                pass
            else:
                workingField.submitter = request.user
                workingField.submitDate = timezone.now()
                workingField.save()


    # Build the arrays that we want to display
    submitterArray = list()
    populatedForms = list()
    submitTimeArray = list()
    for aaf in allAvailableFields:
        populatedForms.append(PdfMonkeyTyperForm(instance=aaf, initial={'typedField': aaf.typedField}))
        submitterArray.append(aaf.submitter)
        if aaf.submitDate:
            submitTimeArray.append(str(aaf.submitDate)[2:10] + "<br />" + str(aaf.submitDate)[12:16])
        else:
            submitTimeArray.append("N/A<br />N/A<br />")

    # Prune off just the filename from the taskImage url
    taskImageBasename = os.path.basename(taskImage.image.url)

    context = {
                  'die': dieObject,
                  'dieImage': taskImage,
                  'dieImageBasename': taskImageBasename,
                  'dieInfoArray': zip(populatedForms, submitterArray, submitTimeArray, range(len(submitTimeArray)))
              }

    return render(request, 'typer/adminSummaryView.html', context)

