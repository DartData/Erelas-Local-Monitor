from guizero import App, Text, PushButton, CheckBox, TextBox


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
    return(server)

    
def hello():
    print("woof")

def writefile(): #write new settings back
    global fileread
    global server
    global path
    global filemon
    global lifemon
    global url
    global urlmon

    fileread = [server, path, filemon, lifemon, url, urlmon]
    file = open("values.txt", "w")
    file.writelines(fileread)
    file.close()

def main():
    global fileread
    global server
    global path
    global filemon
    global lifemon
    global url
    global urlmon

    #read file to start
    readfile()

    #setup app window
    app = App(title="Erelas Local Monitor - Settings")
    title = Text(app, text="Settings", align = "top")
        

    #setup and establih defaults for all
    desttext = Text(app, text="MQTT")
    destbox = TextBox(app, text=server)

    filetext = Text(app, text="File Monitor")
    filebox = TextBox(app, text=path)
    filecheck = CheckBox(app, text="Enable file monitoring")
    filecheck.value = filemon


    lifetext = Text(app, text="RAM & CPU Monitor")
    lifecheck = CheckBox(app, text="Enable RAM & CPU monitoring")
    lifecheck.value = lifemon

    webtext = Text(app, text="Web Monitor")
    webbox = TextBox(app, text=url)
    webcheck = CheckBox(app, text="Enable web monitoring")
    webcheck.value = urlmon

    server = destbox.value
        
    savebutton = PushButton(app, text = "Save", command=writefile)
    quitbutton = PushButton(app, text = "Close", command=app.destroy)
        
    app.display()
