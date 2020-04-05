from pystray import MenuItem as item, Icon as icon, Menu as menu
import pystray
from PIL import Image
import sys

def runtotrue():
    global RUN
    RUN = True

def runtofalse():
    global RUN
    RUN = False



state = False

#______________________________________________________________________
#MAIN PROGRAM

RUN = True

image = Image.open("icon.png")
menu = (item('Run', on_clicked, checked=lambda item:state), item('Quit', quit))
icon = pystray.Icon("name", image,"title",menu)

icon.run()