from datetime import datetime

class DateTime:
    
    def __init__(self):
        super().__init__()
        
    def getDateNameFormat(self):
        now = datetime.now()
<<<<<<< HEAD
        sendTime = now
        now = now.strftime("%d/%m/%Y %H:%M:%S")
        dt_string = now.replace("/", "")
        dt_string = dt_string.replace(" ", "")
        dt_string = dt_string.replace(":", "")
        return dt_string, str(sendTime)
    
=======
        now = now.strftime("%d/%m/%Y %H:%M:%S")
        dt_string = str(now).replace("/", "")
        dt_string = dt_string.replace(" ", "")
        dt_string = dt_string.replace(":", "")
        return dt_string, str(now)

>>>>>>> bbaee747f697fe14ad6ad30700d7d3db2f72049b
    def getSendingDateNameFormat(self, tmpDateTime):
        dt_string = tmpDateTime.replace("/", "")
        dt_string = dt_string.replace(" ", "")
        dt_string = dt_string.replace(":", "")
        return dt_string

            
