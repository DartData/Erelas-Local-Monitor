from time import sleep, ctime
from datetime import datetime
import paho.mqtt.client as mqtt
import psutil
import urllib3
import glob
import os
import sys
import threading

#for gui windows
from guizero import App, Text, PushButton, CheckBox, TextBox, Window

#setting up icon
#import tkinter as Tk # for changing icon


#for menu
from pystray import MenuItem as item, Icon as icon, Menu as menu
import pystray
from PIL import Image

def readfile(): #read saved settings
    global FILEREAD
    global SERVER
    global PATH
    global FILEMON
    global LIFEMON
    global URL
    global URLMON
    global MACHINE
    global FIRSTRUN
 
    try:
        file = open("settings.txt", "r")
        FILEREAD = file.read().splitlines()
        
        #read long strings
        SERVER = FILEREAD[0] #read server line from settings file
        SERVER = SERVER[8:] #read character 8 until the end
        PATH = FILEREAD[1]
        PATH = PATH [11:]
        URL = FILEREAD[4]
        URL = URL[5:]
        MACHINE = FILEREAD[6]
        MACHINE = MACHINE[9:]

        #read on offs and convert to boolean
        #FILMON block
        FILEMON = FILEREAD[2]
        FILEMON = FILEMON[9]
        FILEMON = stringnumtobool(FILEMON,"FILEMON")

        #LIFEMON block
        LIFEMON = FILEREAD[3]
        LIFEMON = LIFEMON[9]
        LIFEMON = stringnumtobool(LIFEMON,"LIFEMON")

        #URLMON
        URLMON = FILEREAD[5]
        URLMON = URLMON[8]
        URLMON = stringnumtobool(URLMON,"URLMON")

        #FIRSTRUN
        FIRSTRUN = FILEREAD[7]
        FIRSTRUN = FIRSTRUN[10:]
        FIRSTRUN = stringnumtobool(FIRSTRUN,"FIRSTRUN")

        file.close()
    except:
        error_message("Reading settings from file")

def stringnumtobool(RAWREAD,ORIGIN): #1 and 0 to boolean converter
    try:
        if RAWREAD == "1":
            OUT = True
        elif RAWREAD == "0":
            OUT = False
        else:
            #error do something
            print("Error converting string number to boolean - characters invalid" + ORIGIN)
            ERROR = "Error converting string number to boolean - characters invalid - from " + ORIGIN
            error_message(ERROR)
        return(OUT)
    except:
        error_message("stringnumtool failed at the first hurdle")

def booltoint(RAWREAD,ORIGIN):
    try:
        if RAWREAD == True:
            OUT = 1
        elif RAWREAD == False:
            OUT = 0
        else:
            #error do something
            print("Error converting boolean to interger - invalid character - from " + ORIGIN)
            ERROR = "Error converting boolean to interger - invalid character - from " + ORIGIN
            error_message(ERROR)
        return(OUT)
    except:
        error_message("booltoint tool failed at the first hurdle")

def file_monitor(): #check logger for files
    global PATH
    area = "file"

    list_of_files = glob.glob(PATH)
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_mod = os.path.getctime(latest_file)
    latest_mod = ctime(latest_mod)
    
    print(latest_file)
    print(latest_mod)

    
        
    MESSAGE = (area + "-" + latest_mod)
    mqtt_post(MESSAGE)

def life_monitor(): #read CPU and RAM
    #get CPU load
    area = "cpul"
    CPULOAD = psutil.cpu_percent(interval=1, percpu=False)
    CPULOAD = float(CPULOAD)
    CPULOAD = str(CPULOAD)
    print(CPULOAD)

    MESSAGE = (area + "-" + CPULOAD)
    mqtt_post(MESSAGE)

    #get memory load
    area = "memr"
    MEMLOAD = psutil.virtual_memory().percent
    MEMLOAD = float(MEMLOAD)
    MEMLOAD = str(MEMLOAD)
    print(MEMLOAD)

    MESSAGE = (area + "-" + MEMLOAD)
    mqtt_post(MESSAGE)

    #get disk usage
    area = "disk"
    DISKUSE = psutil.disk_usage('/').percent
    DISKUSE = float(DISKUSE)
    DISKUSE = str(DISKUSE)
    print(DISKUSE)

    MESSAGE = (area + "-" + DISKUSE)
    mqtt_post(MESSAGE)

def url_monitor(): #check url for existance
    #controls url requests
    http = urllib3.PoolManager()

    #check for http code and get result
    check = http.request('GET', URL,preload_content=False)
    CHECKRESULT = check.status
    print(CHECKRESULT)

    #determine fields to send
    if CHECKRESULT == 200:
        STATUS = "GREEN"
        VALUE = CHECKRESULT
        MEASURE = "HTTP CODE"
    else:
        STATUS = "RED"
        VALUE = CHECKRESULT
        MEASURE = "HTTP CODE"

    #check
    print(STATUS)
    print(VALUE)
    print(MEASURE)

    #transmit result
    area = "urlc"
    MESSAGE = (area + "-" + STATUS)
    mqtt_post(MESSAGE)

def write_log(error): #write local log of errors / start ups
    #print(error)
    now = datetime.now()
    now = str(now)
    log_text = (now, error, r"\n")
    log_text = str(log_text)

    log = open("log.txt", "a")
    log.write(log_text)
    log.close()

def error_message(error):
    #write a log and display an error
    global errorwindow

    error = "Error in " + error

    write_log(error)
    
    errortext = Text(errorwindow, text="Error occured in the following-")
    errortext2 = Text(errorwindow, text=error)
    errortext3 = Text(errorwindow, text="The application must now terminate")
    errortext4 = Text(errorwindow, text="For support please visit https://github.com/moth754/Erelas-Local-Monitor")
    errorbutton = PushButton(errorwindow, text = "Quit", command=quit)
    errorwindow.show()

def mqtt_post(mpayload): #send to mqtt server
    #try:
        global MACHINE
        print("Posting message " + mpayload)
        mqtt_connection()
        print(MACHINE)
        client.publish(MACHINE, mpayload)
    #except:
    #    error_message("mqtt_post failed")

def mqtt_connection():
    global client
    global SERVER
    global MACHINE
    #variables for mqtt and making intial connection
    broker_url = SERVER
    client = mqtt.Client(MACHINE)
    #try: #attempt intial connection
    #client.connect(broker_url, broker_port)
    client.connect(SERVER, port=1883)
    #except: #on error write log and close
    #    print("Error in MQTT connection")
    #    error_message("mqtt connection failed")

def checkingloop():
    global RUN
    firstrunsequence()
    while True:
        if RUN == True:
            readfile()
        else:
            sleep(1)
        while RUN == True:
            print("Running main loop")
            if FILEMON == True:
                file_monitor()
            if LIFEMON == True:
                life_monitor()
            if URLMON == True:
                url_monitor()
            sleep(1)
        else:
            sleep(1)

def closerun():
    try:
        global app
        global RUN
        global settingswindow
        RUN = True
        settingswindow.hide()
    except:
        error_message("closerun failed")

def closenorun():
    try:
        global app
        global settingswindow
        settingswindow.hide()
        app.destroy()
    except:
        error_message("closenorun failed")

def savesettings():
    try:
        #setup the to save list
        #recall firstrun
        global FIRSTRUN

        if FIRSTRUN == True:
            FIRSTRUN = False
            RUN = True
        
        FIRSTRUN = booltoint(FIRSTRUN, "Saving settings")

        #global variables from inputs
        global lifemoncheck
        global urlmoncheck
        global urlinput
        global filemoncheck
        global pathinput
        global serverinput
        global machineinput

        L1 = ("server: " + serverinput.value + "\n").rstrip()
        L2 = ("directory: " + pathinput.value  + "\n").rstrip()
        L3 = "filemon: " + str(filemoncheck.value)  + "\n"
        L4 = "lifemon: " + str(lifemoncheck.value)  + "\n"
        L5 = "url: " + urlinput.value  + "\n"
        L6 = "urlmon: " + str(urlmoncheck.value)  + "\n"
        L7 = "machine: " + machineinput.value  + "\n"
        L8 = "firstrun: " + str(FIRSTRUN)

        TOSAVE = [L1,L2,L3,L4,L5,L6,L7,L8]

        file = open("settings.txt", "w")
        file.writelines(TOSAVE)
        file.close()
    
    except:
        error_message("savesettings failed")

def resetsettings(): #sets all the UI input fields to the same as previously saved in the settings file
    try:
        sleep(1)
        global app
        readfile() # re read original settings

        ORIGIN = "Reset Settings Function" #for error handling

        #global all necessarg
        global LIFEMON_INT
        global FILEMON_INT
        global URLMON_INT
        global PATH
        global MACHINE
        global URL
        global app
        global lifemoncheck
        global urlmoncheck
        global urlinput
        global filemoncheck
        global pathinput
        global SERVER
        global serverinput
        global machineinput

        #convert all the tick boxes
        LIFEMON_INT = booltoint(LIFEMON, ORIGIN)
        FILEMON_INT = booltoint(FILEMON, ORIGIN)
        URLMON_INT = booltoint(URLMON, ORIGIN)
        
        #tick box repopulating
        lifemoncheck.value = LIFEMON_INT
        urlmoncheck.value = URLMON_INT
        filemoncheck.value = FILEMON_INT
        
        #textbox repopulating
        serverinput.value = SERVER
        urlinput.value = URL
        pathinput.value = PATH
        machineinput.value = MACHINE

        #app.update()
    
    except:
        error_message("resetsettings failed")

def settingsmenu():
    #try:
        #change settings in here
        global RUN
        global MACHINE
        global LIFEMON_INT
        global FILEMON_INT
        global URLMON_INT
        global PATH
        global URL
        global app
        global lifemoncheck
        global urlmoncheck
        global urlinput
        global filemoncheck
        global pathinput
        global SERVER
        global serverinput
        global machineinput
        global firstwindow
        global settingswindow

        RUN = False

        readfile()

        ORIGIN = "Settings Menu"
        #convert variables for use
        LIFEMON_INT = booltoint(LIFEMON, ORIGIN)
        FILEMON_INT = booltoint(FILEMON, ORIGIN)
        URLMON_INT = booltoint(URLMON, ORIGIN)
        
        #setup settings UI
        #settingswindow = Window(app, title="Erelas monitoring system - settings")

        #machine name settings
        machinetext = Text(settingswindow, text = "Machine name", grid=[0,0])
        machineinput = TextBox(settingswindow, grid= [1,0])
        machineinput.value = MACHINE
        
        #server settings
        servertext = Text(settingswindow, text = "Server IP address", grid=[0,1])
        serverinput = TextBox(settingswindow, grid=[1,1])
        serverinput.value = SERVER

        #life monitor section
        lifemontext = Text(settingswindow, text = "Activate CPU / RAM / disk monitor", grid=[0,2])
        lifemoncheck = CheckBox(settingswindow, text = "Report CPU use", grid=[1,2])
        lifemoncheck.value = LIFEMON_INT

        #url monitor section
        urlmontext = Text(settingswindow, text = "Activate URL monitor", grid=[0,3])
        urlmoncheck = CheckBox(settingswindow, text = "Report URL status", grid = [1,3])
        urlmoncheck.value = URLMON_INT
        urlinputtext = Text(settingswindow, text = "Enter URL to monitor", grid=[0,4])
        urlinput = TextBox(settingswindow, grid=[1,4])
        urlinput.value = URL

        #file monitor sections
        filemontext = Text(settingswindow, text = "Activate file modified monitor", grid=[0,5])
        filemoncheck = CheckBox(settingswindow, text = "Report most recent file update", grid=[1,5])
        filemoncheck.value = FILEMON_INT
        pathinputtext = Text(settingswindow, text = "Path to monitor files at", grid=[0,6])
        pathinput = TextBox(settingswindow, grid=[1,6])
        pathinput.value = PATH

        if FIRSTRUN == True:
            firstwindow.hide()
            savebutton = PushButton(settingswindow, text="Save and run", command = savesettings, grid=[0,7])
            quitbutton = PushButton(settingswindow, text="Quit", command= quit, grid= [1,7])
        else:
            #save section
            savebutton = PushButton(settingswindow, text="Save and apply changes", command = savesettings, grid=[0,7])
            resetbutton = PushButton(settingswindow, text="Discard changes and reset to previous values", command= resetsettings, grid = [1,7])

            #quit section
            closerunbutton = PushButton(settingswindow, text="Close and run", command= closerun, grid=[0,8])
            closenorunbutton = PushButton(settingswindow, text="Close and don't run", command= closenorun, grid=[1,8])
        settingswindow.show()

    #except:    
        #error_message("Settingsmenu has failed")

def about():
    global aboutwindow
    try:
        abouttext = Text(aboutwindow, text="About")
        aboutbutton = PushButton(aboutwindow, text = "Close", command=aboutwindow.hide)
        aboutwindow.show()
    except:
        error_message("about failed")

def on_clicked(icon, item):
    try:
        global RUN
        RUN = not item.checked
        print(RUN)
    
    except:
        error_message("on_clicked failed")

def quit():
    write_log("Program ended")
    os._exit(0)

def traymenu():
    global RUN
    try:
        image = Image.open("icon.png")
        menu = (
            item('Run', on_clicked, checked=lambda item:RUN), 
            item("Settings", settingsmenu),
            item("About", about), 
            item('Quit', quit)
            )
        icon = pystray.Icon("name", image,"title",menu)
        icon.run()

    except:
        error_message("traymenu failed")

def firstrunsequence():
    global RUN
    RUN = False
    splashscreen()
    if FIRSTRUN == True:
        firsttext = Text(firstwindow, text="First Run")
        firstclose = PushButton(firstwindow, text = "Quit", command=quit)
        firstbutton = PushButton(firstwindow, text = "Setup", command=settingsmenu)
        firstwindow.show()
        write_log("First time run")
    else:
        RUN = True
        write_log("Program started and RUN == True")

def splashscreen():
    #show splashscreen
    splashwindow = Window(app, "Erelas monitoring system", width=450, height = 100)
    splashtext = Text(splashwindow, text="Device status monitored by Erelas monitoring system")
    splashtext2 = Text(splashwindow, text = "https://github.com/moth754/Erelas-Local-Monitor")
    splashwindow.show()
    sleep(3)
    splashwindow.hide()

#______________________________________________________________________
#MAIN PROGRAM

readfile() #read the settings

RUN = True

#setup the ui
app = App(title = "Erelas monitoring system", visible = False)
#app.tk.iconbitmap("icon.ico")

settingswindow = Window(app, title="Erelas monitoring system - settings", layout="grid")
settingswindow.hide()
aboutwindow = Window(app, title= "About")
aboutwindow.hide()
errorwindow = Window(app, title= "Error occured")
errorwindow.hide()
firstwindow = Window(app, title="Erelas monitoring system - first run")
firstwindow.hide()

#intiate the threads
uithread = threading.Thread(target=traymenu)
uithread.start()

checkthread = threading.Thread(target=checkingloop)
checkthread.start()

#intitiate display
app.display()