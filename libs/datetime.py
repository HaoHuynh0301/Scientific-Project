from datetime import datetime

class DateTime:
    def __init__(self):
        super().__init__()
        
    def getDateNameFormat(self):
        now = datetime.now()
        sendTime = now
        now = now.strftime("%Y/%m/%d %H:%M:%S")
        dt_string = now.replace("/", "")
        dt_string = dt_string.replace(" ", "")
        dt_string = dt_string.replace(":", "")
        return dt_string, str(sendTime)
    
    def getSendingDateNameFormat(self, tmpDateTime):
        dt_string = tmpDateTime.replace("/", "")
        dt_string = dt_string.replace(" ", "")
        dt_string = dt_string.replace(":", "")
        return dt_string
    
    def getDateNameFormat2(self, time):
        dt_string = time.replace("/", "")
        dt_string = dt_string.replace(" ", "")
        dt_string = dt_string.replace(":", "")
        dt_string = dt_string.replace("-", "")
        dt_string = dt_string[:14]
        return dt_string

            
