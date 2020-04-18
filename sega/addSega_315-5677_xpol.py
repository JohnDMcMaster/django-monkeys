import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monkeys.settings")

import django
django.setup()

from typer.models import Die, DieImage, TypedDie

# Add the die
d = Die(name="Sega_315-5677_xpol")
d.save()

# Add its instructions (with custom [[[IMAGE_NAME (WIDTH HEIGHT)]]] markup)
d.instructions = """
    Thank you for your interest in the sipr0n crowdsource project!
    We appreciate your time and want to make the most of it.
    Please review the below instructions to ensure we are able to use your results.<br />
    <br />
    [[[InstructionImage_00 250 250]]]
    [[[InstructionImage_01 250 250]]]<br />
    <br />
    What: these images are Fujitsu TGP DSPs from Sega Model 1 and 2 arcade systems.
    Accurately recovering these ROMs helps better understand their custom 3d video hardware.<br />
    <br />
    You will get a task that looks something like this:<br />
    [[[InstructionImage_02]]]<br />
    <br />
    Type an 8x8 grid of 1's and 0's where a 1 is a lighter square and a 0 is a darker square.
    For example:<br />
    [[[InstructionImage_03]]]<br />
    <br />
    If a bit is hard to read make a best guess.
    If you believe your guess would be completely random, respond with a ?.
    But remember: the whole point of this is to use more advanced human pattern matching where computer vision fails.
    Please try to make a guess even if you are uncertain.
    For example, one bit in the image is dirty:<br />
    [[[InstructionImage_04]]]<br />
    <br />
    But the bit can still be clearly seen and so was filled in.<br />
    <br />
    It's possible to get a task with all 0's (ie completely black like below) or all 1's.
    That's fine, just respond appropriately. Here's all 0's:<br />
    [[[InstructionImage_05]]]<br />
    <br />
    Remember: you can copy and paste as needed.<br />
    <br />
    Still have questions or suggestions?
    Try the contact form at the top of the page.
    We'll get back to you as soon as we are able.
    """

# And the images that go with the instructions
for i in range(6):
    n = "InstructionImage_%02d" % i
    i = "sega_315-5677_xpol/instructions_%02d.png" % i
    d.instructionsimage_set.create(die=d, name=n, image=i)
d.save()

# Add the images to the die
for x in range(32):
    for y in range(32):
        imageName = "sega_315-5677_xpol/sega_315-5677_xpol_%02d_%02d.png" % (x, y)
        di = DieImage(die=d, cropCol=x, cropRow=y, image=imageName, bitWidth=8, bitHeight=8)
        di.save()
	
        # Add the empty typing fields to this new die image
        for i in range(5):
            td = di.typeddie_set.create(dieImage=di)
