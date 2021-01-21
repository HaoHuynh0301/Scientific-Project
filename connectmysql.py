import time
from datetime import datetime
import mysql.connector
from mysql.connector import errorcode


def connect_to_Mysql():
    try:
        cnx=mysql.connector.connect(user='root', password='hao152903', database='ras')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
        else:
            print(err)
    else:
        cnx.close()
        
def add_status(status, temp_id, ras_id, cnx):
    cursor=cnx.cursor()
    add_status=("INSERT INTO status VALUES (%s, %s, %s)")
    data_status=(status, temp_id, datetime.now())
    cursor.execute(add_status, data_status)
    cnx.commit()

    