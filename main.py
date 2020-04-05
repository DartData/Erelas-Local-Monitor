from time import sleep
from datetime import datetime
import paho.mqtt.client as mqtt
import psutil
import urllib3
import glob
import os
import sys
import threading

#for gui windowa
from guizero import App, Text, PushButton, CheckBox, TextBox

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
    latest_file = max(list_of_files, key=os.PATH.getctime)
    latest_mod = os.PATH.getctime(latest_file)
    #latest_mod = datetime.fromtimestamp(latest_mod).strftime('%Y-%m-%d %H:%M:%S')
    print(latest_file)
    print(latest_mod)
        
    mtopic = (MACHINE + "-" + area)
    print(mtopic)
    mqtt_post(mtopic,latest_mod)

def life_monitor(): #read CPU and RAM
    #get CPU load
    area = "cpu"
    CPULOAD = psutil.cpu_percent(interval=1, percpu=False)
    CPULOAD = float(CPULOAD)
    print(CPULOAD)

    mtopic = (MACHINE + "-" + area)
    print(mtopic)
    CPULOAD = str(CPULOAD)
    mqtt_post(mtopic,CPULOAD)

    #get memory load
    area = "mem"
    MEMLOAD = psutil.virtual_memory().percent
    MEMLOAD = float(MEMLOAD)
    print(MEMLOAD)

    mtopic = (MACHINE + "-" + area)
    print(mtopic)
    MEMLOAD = str(MEMLOAD)
    mqtt_post(mtopic,MEMLOAD)

    #get disk usage
    area = "disk"
    DISKUSE = psutil.disk_usage('/').percent
    DISKUSE = float(DISKUSE)
    print(DISKUSE)

    mtopic = (MACHINE + "-" + area)
    print(mtopic)
    DISKUSE = str(DISKUSE)
    mqtt_post(mtopic,DISKUSE)

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
    area = "url"
    mtopic = (MACHINE + "-" + area)
    print(mtopic)
    mqtt_post(mtopic,STATUS)

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

    error = "Error in " + error

    write_log(error)
    
    errorapp = App(title= "Error occured")
    errortext = Text(errorapp, text="Error occured in the following-")
    errortext2 = Text(errorapp, text=error)
    errortext3 = Text(errorapp, text="The application must now terminate")
    errortext4 = Text(errorapp, text="For support please visit https://github.com/moth754/Erelas-Local-Monitor")
    errorbutton = PushButton(errorapp, text = "Quit", command=quit)
    errorapp.display()

def mqtt_post(mtopic,mpayload): #send to mqtt server
    try:
        print("Posting message from " + mtopic)
        print(mpayload)
        mqtt_connection()
        client.publish(topic=mtopic, payload=mpayload, qos=0, retain=False)
    except:
        error_message("mqtt_post failed")

def mqtt_connection():
    global client
    global SERVER
    #variables for mqtt and making intial connection
    broker_url = SERVER
    broker_port = 1883
    client = mqtt.Client()
    try: #attempt intial connection
        client.connect(broker_url, broker_port)
    except: #on error write log and close
        print("Error in MQTT connection")
        error_message("mqtt connection failed")

def checkingloop():
    global RUN
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
        RUN = True
        app.destroy()
    except:
        error_message("closerun failed")

def closenorun():
    try:
        global app
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

        L1 = "server: " + serverinput.value + " \n"
        L2 = "directory: " + pathinput.value  + " \n"
        L3 = "filemon: " + str(filemoncheck.value)  + " \n"
        L4 = "lifemon: " + str(lifemoncheck.value)  + " \n"
        L5 = "url: " + urlinput.value  + " \n"
        L6 = "urlmon: " + str(urlmoncheck.value)  + " \n"
        L7 = "machine: " + machineinput.value  + " \n"
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
    try:
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
        global firstapp

        RUN = False

        readfile()

        ORIGIN = "Settings Menu"
        #convert variables for use
        LIFEMON_INT = booltoint(LIFEMON, ORIGIN)
        FILEMON_INT = booltoint(FILEMON, ORIGIN)
        URLMON_INT = booltoint(URLMON, ORIGIN)
        
        #setup settings UI
        app = App(title="Erelas Settings")

        #machine name settings
        machineinput = TextBox(app)
        machineinput.value = MACHINE
        
        #server settings
        serverinput = TextBox(app)
        serverinput.value = SERVER

        #life monitor section
        lifemoncheck = CheckBox(app, text = "Report CPU use")
        lifemoncheck.value = LIFEMON_INT

        #url monitor section
        urlmoncheck = CheckBox(app, text = "Report URL status")
        urlmoncheck.value = URLMON_INT
        urlinput = TextBox(app)
        urlinput.value = URL

        #file monitor sections
        filemoncheck = CheckBox(app, text = "Report most recent file update")
        filemoncheck.value = FILEMON_INT
        pathinput = TextBox(app)
        pathinput.value = PATH

        if FIRSTRUN == True:
            firstapp.destroy()
            savebutton = PushButton(app, text="Save and run", command = savesettings)
            quitbutton = PushButton(app, text="Quit", command= quit)
        else:
            #save section
            savebutton = PushButton(app, text="Save and apply changes", command = savesettings)
            resetbutton = PushButton(app, text="Discard changes and reset to previous values", command= resetsettings)

            #quit section
            closerunbutton = PushButton(app, text="Close and run", command= closerun)
            closenorunbutton = PushButton(app, text="Close and don't run", command= closenorun)
        
        
        app.display()
    
    except:
        error_message("Settingsmenu has failed")

def about():
    try:
        firstapp = App(title= "About")
        abouttext = Text(firstapp, text="About")
        aboutbutton = PushButton(firstapp, text = "Close", command=firstapp.destroy)
        firstapp.display()
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

#______________________________________________________________________
#MAIN PROGRAM

#first run
readfile()

if FIRSTRUN == True:
    firstapp = App(title= "First Run")
    firsttext = Text(firstapp, text="First Run")
    firstclose = PushButton(firstapp, text = "Quit", command=quit)
    firstbutton = PushButton(firstapp, text = "Setup", command=settingsmenu)
    firstapp.display()
    write_log("First time run")
else:
    RUN = True
    write_log("Program started and RUN == True")

uithread = threading.Thread(target=traymenu)
uithread.start()

checkthread = threading.Thread(target=checkingloop)
checkthread.start()