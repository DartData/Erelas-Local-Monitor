from pystray import MenuItem as item
import pystray
from PIL import Image

def action():
    pass

image = Image.open("icon.png")
menu = (item('name', action), item('name', action))
icon = pystray.Icon("name", image, "title", menu)
icon.run()
