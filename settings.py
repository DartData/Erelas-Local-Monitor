from guizero import App, Text, PushButton

global run
run = True

def readfile():
    #temporary placeholders
    server = "192.168.1.2" #MQTT destination
    fle_mon = False #file monitor
    lfe_mon = False #life monitor
    web_addr = "www.google.com" #address to monitor
    web_mon = False #web monitor

def hello():
    print("woof")

def main(run):
    run = False
    app = App(title="Erelas Local Monitor - settings")
    title = Text(app, text="Settings", align = "top")
    app.display()


main(run)
