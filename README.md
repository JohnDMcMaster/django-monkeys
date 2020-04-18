# django-monkeys
A framework for getting input from multiple users in an online environment.

A django project named monkeys that handles login and boiler-plate stuff, 
and an app named typer that lets the user type what they see in a given image.


## Installation

Using:
  * Python 3.5+
    * "ImportError: No module named 'secrets'": 3.6?
  * Django 1.11


Dependencies:

```
sudo apt-get install -y python3-pip
sudo pip3 install django-registration
   issues....
   sudo pip3 install django-registration==2.4.1 
sudo pip3 install Pillow
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

Cutting up the jpeg is done in the image chopper program. There's an option to export a series of images. Gotta draw lines first, etc

https://github.com/andrew-gardner/die-toy

```
sudo apt-get install -y git
git clone https://github.com/andrew-gardner/die-toy.git
sudo apt install -y cmake
sudo apt-get install -y qtbase5-dev
    fixes: Qt5NetworkConfig.cmake
sudo apt-get install -y libopencv-dev
    ubuntu 16.04 : packages broken, couldn't even install
    ubuntu 18.04 (3.2.0): ok
        OpenCV2_CORE_INCLUDE_DIR:PATH=/usr/include/opencv2/core
    ubuntu 20.04 (3.2.0): cmake had trouble finding. Something about cv4? 
        /usr/include/opencv4/opencv2/core
mkdir build
cd build
cmake ..
make

./dieToy -h
Usage: ./dieToy [options]
DieToy : An application to manipulate images of chip dies.

Options:
  -h, --help                       Displays this help.
  -v, --version                    Displays version information.
  -i, --image <filename>           Die image to load.
  -d, --dieDescription <filename>  Die description file to load.
```

```
python testAddSega_315-[WHATEVER]_xpol.py
```

## Schema change

Need to apply migrations

python3 manage.py makemigrations

```
$ python3 manage.py makemigrations
Migrations for 'typer':
  typer/migrations/0003_auto_20200417_0639.py
    - Create model Pdf
    - Create model PdfImage
    - Create model TypedPdf
    - Remove field instructionsImage from die
```

View database with sqlitebrowser


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


## Related projects

Ultimately this project gets momentum because its what we're familiar with.
But here are some related projects that you might be interested in

https://pybossa.com/

