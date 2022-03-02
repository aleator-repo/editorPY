#Imports de la aplicacion actual
import json
import uopy

#Imports del sistema
import os

def connect():
    with open(os.getcwd()+"/config/dbConfig.json") as f:
        env_vars = json.loads(f.read())
        try:
            hostIP   = env_vars["hostIP"]
            user     = env_vars["user"]
            password = env_vars["password"]
            account  = env_vars["account"]
        except Exception as error:
            print("Error: Debe setear los datos de la base de datos en el archivo dbConfig.json")
            exit()

    try:
        Session =  uopy.connect(host=hostIP, user=user, password=password, account=account, encoding='cp1252')
        return Session
        
    except uopy.UOError as e:
        print(str(e))
        return (str(e))

def getConnectionDB(session):
    try:
        if (session.health_check()):
            return session
    except Exception as e:
        session = connect()
        return session

