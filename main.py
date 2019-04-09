from pystray import MenuItem as item
import pystray
from PIL import Image
import settings


#set default variables
global run
global start_stop_label
run = True
start_stop_label = 'Stop'



def quit():
    print("quit")
    exit()

def settings():
    print("settings")
    settings.main()

def process():
    global run
    if run == True:
        print("Stopped")
        run = False
    elif run == False:
        print("Started")
        run = True
    icon.update_menu()

#setup icon in system tray
image = Image.open("icon.png")
menu = (item('Process', process, checked=lambda item:run), item('Settings', settings), item('Quit', quit))
icon = pystray.Icon("name", image,"title",menu)

#run the program
icon.run()
