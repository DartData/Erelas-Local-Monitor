import glob
import os
from time import sleep, ctime

PATH = r"C:\Users\timmo\Downloads\*"

list_of_files = glob.glob(PATH)
latest_file = max(list_of_files, key=os.path.getctime)
latest_mod = os.path.getctime(latest_file)
latest_mod = ctime(latest_mod)
#latest_mod = datetime.fromtimestamp(latest_mod).strftime('%Y-%m-%d %H:%M:%S')
print(latest_file)
print(latest_mod)