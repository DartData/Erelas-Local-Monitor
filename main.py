from time import sleep
from datetime import datetime
import paho.mqtt.client as mqtt
import psutil
import urllib3
import glob
import os


#variables for mqtt and making intial connection
broker_url = "192.168.1.108"
broker_port = 1883

client = mqtt.Client()

try: #attempt intial connection
    client.connect(broker_url, broker_port)
except: #on error write log and close
    print("Error in MQTT connection")
    write_log("MQTT Connection Error")
    exit()

#variables per PC
path = r"C:\Users\timmo\Downloads\*" # * indicates all file types will be scanned
url = "http://stream.crossrhythms.co.uk/plymouth/hq.mp3" #url to check
computer = "DAD1"

def readfile(): #read saved settings currently not used
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

def file_monitor(): #check logger for files
    area = "file"
    list_of_files = glob.glob(path) 
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_mod = os.path.getctime(latest_file)
    #latest_mod = datetime.fromtimestamp(latest_mod).strftime('%Y-%m-%d %H:%M:%S')
    print(latest_file)
    print(latest_mod)
        
    mtopic = (computer + "-" + area)
    print(mtopic)
    mqtt_post(mtopic,latest_mod)


def life_monitor(): #read CPU and RAM
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

def url_monitor(): #check url for existance
    #controls url requests
    http = urllib3.PoolManager()

    #check for http code and get result
    check = http.request('GET', url,preload_content=False)
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
    client.publish(topic=mtopic, payload=mpayload, qos=0, retain=False)
    
#on off switches
file_switch = False
life_switch = True
url_switch = False

#main loop
while True:
    print("Running main loop")
    if file_switch == True:
        try:
            file_monitor()
        except:
            print("Error in file monitor execution")
            write_log("File Monitor Error")
    if life_switch == True:
        try:
            life_monitor()
        except:
            print("Error in life monitor execution")
            write_log("Life Monitor Error")
    if url_switch == True:
        try:
            url_monitor()
        except:
            print("Error in url monitor execution")
            write_log("URL Monitor Error")

