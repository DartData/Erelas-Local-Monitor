from pystray import MenuItem as item
import pystray
from PIL import Image
from time import sleep


#set default variables
global run
global start_stop_label
run = False
start_stop_label = 'Stop'

def readfile(): #read saved settings
    global fileread
    global server
    global path
    global filemon
    global lifemon
    global url
    global urlmon

    file = open("values.txt", "r")
    fileread = file.read().splitlines()
    server = fileread[0]
    path = fileread[1]
    filemon = fileread[2]
    lifemon = fileread[3]
    url = fileread[4]
    urlmon = fileread[5]
    file.close()

def quit():
    print("quit")
    exit()

def process():
    global run
    if run == True:
        print("Stopped")
        run = False
    elif run == False:
        print("Started")
        run = True
    icon.update_menu()

    while run == True:
        print(server)

def read_cpu_ram():
    if run == True:
        print("stuff")
    elif run == False:
        sleep(0.1)

#setup icon in system tray
readfile()
image = Image.open("icon.png")
menu = (item('Process', process, checked=lambda item:run), item('Refresh Settings', readfile), item('Quit', quit))
icon = pystray.Icon("name", image,"title",menu)

#run the program
icon.run()