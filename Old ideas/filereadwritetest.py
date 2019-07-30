file = open("values.txt", "r")
fileread = file.read().splitlines()
print(fileread)
server = fileread[0]
path = fileread[1]
filemon = fileread[2]
lifemon = fileread[3]
url = fileread[4]
urlmon = fileread[5]
print(server)