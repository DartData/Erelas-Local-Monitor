import urllib3

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