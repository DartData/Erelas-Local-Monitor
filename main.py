from time import sleep
from datetime import datetime
import paho.mqtt.client as mqtt
import psutil
import urllib3
import glob
import os
import sys
import threading
from guizero import App, Text, PushButton

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
    FILEMON = readconvert(FILEMON,"FILEMON")

    #LIFEMON block
    LIFEMON = FILEREAD[3]
    LIFEMON = LIFEMON[9]
    LIFEMON = readconvert(LIFEMON,"LIFEMON")

    #URLMON
    URLMON = FILEREAD[5]
    URLMON = URLMON[8]
    URLMON = readconvert(URLMON,"URLMON")


    file.close()

def readconvert(RAWREAD,ORIGIN): #1 and 0 to boolean converter
    if RAWREAD == "1":
        OUT = True
    elif RAWREAD == "0":
        OUT = False
    else:
        #error do something
        print("Error reading " + ORIGIN)
        ERROR = "FILEMON " + ORIGIN
        write_log(ERROR)
    return(OUT)

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

def mqtt_post(mtopic,mpayload): #send to mqtt server
    print("Posting message from " + mtopic)
    print(mpayload)
    mqtt_connection()
    client.publish(topic=mtopic, payload=mpayload, qos=0, retain=False)

def mqtt_connection():
    global client
    #variables for mqtt and making intial connection
    broker_url = "192.168.1.116"
    broker_port = 1883
    client = mqtt.Client()
    try: #attempt intial connection
        client.connect(broker_url, broker_port)
    except: #on error write log and close
        print("Error in MQTT connection")
        write_log("MQTT Connection Error")

def checkingloop():
    global RUN
    if RUN == True:
        readfile()
        sleep(1)
    else:
        sleep(1)
    
    while RUN == True:
        sleep(1)
        print("Running main loop")
        if FILEMON == True:
            try:
                file_monitor()
            except:
                print("Error in file monitor execution")
                write_log("File Monitor Error")
        if LIFEMON == True:
            try:
                life_monitor()
            except:
                print("Error in life monitor execution")
                write_log("Life Monitor Error")
        if URLMON == True:
            try:
                url_monitor()
            except:
                print("Error in url monitor execution")
                write_log("URL Monitor Error")

def runtotrue():
    global RUN
    RUN = True

def runtofalse():
    global RUN
    RUN = False

def settingsmenu():
    #change settings in here
    runtofalse()
    app = App(title="Erelas Settings")
    closebutton = PushButton(app, text="Close", command=)
    app.display()

def on_clicked(icon, item):
    global RUN
    RUN = not item.checked
    print(RUN)

def quit():
    os._exit(0)

def traymenu():
    image = Image.open("icon.png")
    menu = (item('Run', on_clicked, checked=lambda item:RUN), item("Settings", settingsmenu), item('Quit', quit))
    icon = pystray.Icon("name", image,"title",menu)
    icon.run()

#______________________________________________________________________
#MAIN PROGRAM

RUN = True

uithread = threading.Thread(target=traymenu)
uithread.start()

checkthread = threading.Thread(target=checkingloop)
checkthread.start()

