from guizero import App, Text, PushButton

def open_settings(): #what to do when settings button is pressed
    text.value = "hello world"

#app setup
app = App(title="Erelas Local Monitor")
text = Text(app)

#buttons
button = PushButton(app, text="Settings", command=open_settings)

#intialise app
app.display()
