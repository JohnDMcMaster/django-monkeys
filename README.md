# django-monkeys
A framework for getting input from multiple users in an online environment.

A django project named monkeys that handles login and boiler-plate stuff, 
and an app named typer that lets the user type what they see in a given image.


## Installation

Using:
  * Python 3.5+
  * Django 1.11


Dependencies:

```
pip install django-registration
pip install Pillow
```

Edit settings.py

```
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'blahblah@gmail.com'
EMAIL_HOST_PASSWORD = 'blahblahblah'
EMAIL_USE_TLS = True
```

Also maybe monkeys/views.py

    send_mail(subject, message, fromEmail, ['blah@googlegroups.com'])


## Creating jobs


## Running

    python manage.py runserver 0.0.0.0:8000

## Post processing

Processing a completed die

Start by attempting extraction:

    python tools/db2bin.py  my_chip

You will likely get some conflicts that can't be automatically resolved
Create a conflict resolution file and re-run:
python tools/db2bin.py --cf my.pyl  my_chip

Optional: compare vs reference ROM: python tools/romdiff.py my_cs.bin my_ref.bin my_cs-ref.png

