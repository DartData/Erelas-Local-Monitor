import glob
import os

path = r"C:\Users\timmo\Downloads\*"

list_of_files = glob.glob(path) # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
print(latest_file)