from time import sleep
import paho.mqtt.publish as publish

server = "192.168.0.1"
channel = "Test"
path = "C:\Test"
filemon = 0
lifemon = 1
url = "https://www.google.com"
urlmon =  0


def readfile(): #read saved settings
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

def file_monitor():
    if filemon == 1:
        print("stuff")
    elif filemon == 0:
        sleep(0.1)

def life_monitor():
    if lifemon == 1:
        print("stuff")
    elif lifemon == 0:
        sleep(0.1)

def url_mon():
    if urlmon == 1:
        print("stuff")
    elif urlmon == 0:
        sleep(0.1)

def write_log():
    print("Stuff")

def mqtt_post():
    print("Stuff")
    MQTT_SERVER = server
    MQTT_PATH = channel
    publish.single(MQTT_PATH, "Hello World!", hostname=MQTT_SERVER)

#setup icon in system tray
mqtt_post()
