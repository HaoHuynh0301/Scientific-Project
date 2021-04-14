from datetime import datetime

class DateTime:
    
    def __init__(self):
        super().__init__()
        
    def getDateNameFormat(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dt_string = dt_string.replace("/", "")
        dt_string = dt_string.replace(" ", "")
        dt_string = dt_string.replace(":", "")
        return dt_string, str(now)

    def getSendingDateNameFormat(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        dt_string = dt_string.replace("/", "")
        dt_string = dt_string.replace(" ", "")
        dt_string = dt_string.replace(":", "")
        return dt_string

            
