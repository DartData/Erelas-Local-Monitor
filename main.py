from time import sleep
import paho.mqtt.client as mqtt
import psutil
import urllib3
import glob
import os

#variables for mqtt and making intial connection
broker_url = "192.168.1.108"
broker_port = 1883

client = mqtt.Client()
client.connect(broker_url, broker_port)

#placeholders
mtopic = "helloworld"
mpayload = "100"

#variables per PC
channel = r"hello/world"
path = r"C:\Users\timmo\Downloads\*" # * indicates all file types will be scanned
filemon = 0
lifemon = 1
url = "https://www.google.com"
urlmon =  0
computer = "DAD1"

def readfile(): #read saved settings currently not used
    global fileread
    global server
    global path
    global filemon
    global lifemon
    global url
    global urlmon
    global channel

    file = open("values.txt", "r")
    fileread = file.read().splitlines()
    server = fileread[0]
    path = fileread[1]
    filemon = fileread[2]
    lifemon = fileread[3]
    url = fileread[4]
    urlmon = fileread[5]
    channel = fileread[6]
    file.close()

def file_monitor(): #check logger for files
    if filemon == 1:
        list_of_files = glob.glob(path) 
        latest_file = max(list_of_files, key=os.path.getctime)
        print(latest_file)
        

    elif filemon == 0:
        sleep(0.1)

def life_monitor(): #read CPU and RAM
    if lifemon == 1:
        #get CPU load
        area = "cpu"
        CPULOAD = psutil.cpu_percent(interval=1, percpu=False)
        CPULOAD = float(CPULOAD)
        print(CPULOAD)

        mtopic = (computer + "-" + area)
        print(mtopic)
        CPULOAD = str(CPULOAD)
        mqtt_post(mtopic,CPULOAD)

        #get memory load
        area = "mem"
        MEMLOAD = psutil.virtual_memory().percent
        MEMLOAD = float(MEMLOAD)
        print(MEMLOAD)

        mtopic = (computer + "-" + area)
        print(mtopic)
        MEMLOAD = str(MEMLOAD)
        mqtt_post(mtopic,MEMLOAD)

        #get disk usage
        area = "disk"
        DISKUSE = psutil.disk_usage('/').percent
        DISKUSE = float(DISKUSE)
        print(DISKUSE)

        mtopic = (computer + "-" + area)
        print(mtopic)
        DISKUSE = str(DISKUSE)
        mqtt_post(mtopic,DISKUSE)

    elif lifemon == 0:
        sleep(0.1)

def url_mon(): #check url for existance
    if urlmon == 1:
        #controls url requests
        http = urllib3.PoolManager()

        #check for http code and get result
        check = http.request('GET', 'http://stream.crossrhythms.co.uk/plymouth/hq.mp3',preload_content=False)
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
        mtopic = (computer + "-" + area)
        print(mtopic)
        mqtt_post(mtopic,STATUS)

    elif urlmon == 0:
        sleep(0.1)

def write_log(): #write local log of errors / start ups
    print("Stuff")

def mqtt_post(mtopic,mpayload): #send to mqtt server
    print("Posting message from " + mtopic)
    client.publish(topic=mtopic, payload=mpayload, qos=2, retain=False)

#setup icon in system tray
life_monitor()
