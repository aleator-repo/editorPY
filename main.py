#Imports de la aplicacion actual
from logging import exception
from flask import Flask, request, Blueprint,jsonify, render_template,session
import json
import uopy
from uopy import UOError , Command, List
from uopy import EXEC_MORE_OUTPUT
from datetime import datetime

#Imports del sistema
import os

#Imports de secciones
from database import getConnectionDB

app = Flask(__name__)

ses = ""
ipPort = "localhost:5001"

def getSelectList( thelistcommand, session, sorted = 1):
    
    cmd = Command(session=session)
    cmd.command_text = "CLEARSELECT"
    cmd.run()
    cmd.command_text = thelistcommand
    cmd.run()
	
    theRtnList = []
    try:
        theList = List(0, session=session)
        theidList = theList.read_list()
        
        for each in theidList:
            if len(each) > 0:
                theRtnList.extend( [each] )

        if (sorted):
            theRtnList.sort()

        return theRtnList
    except UOError as e:
        return str(e)

def getDict( table , session):
    
    cmd = Command(session=session)
    cmd.command_text = "CLEARSELECT"
    cmd.run()
    cmd.command_text = "LIST DICT " +table.upper()
    cmd.run()
    toRet = {}
    if (cmd.at_system_return_code >= 0):
        texto = cmd.response
        texto = texto.split("\r\n\r\n")[2]
        lineas = texto.split("\r\n")

        for i,linea in enumerate(lineas):
            nombre = linea[0:14]
            tipo   = linea[15:16]
            formato = linea[-1:]
            conversion = linea[36:41]
            
            lineaStrip = " ".join(linea.split()).split(" ")
            if (tipo.strip() != ''):    
                
                try: 
                    number = linea[18:21]
                    number = number.strip()
                    number = int(number)
                except:
                    pass

                try: 
                    conversion = conversion.strip()
                except:
                    pass
                
                nombre = lineaStrip[0]
                try:
                    tipo = lineaStrip[1]
                except:
                    pass

                if number != '':
                    try: 
                        toRet[number]['name'] =  nombre
                    except:
                        toRet[number] =  {}
                        toRet[number]['name'] =  nombre
                        toRet[number]['type'] =  tipo
                        toRet[number]['number'] =  number
                        toRet[number]['format'] =  formato
                        toRet[number]['conversion'] =  conversion
            else: 
                try: 
                    nombre = nombre.strip()
                    #toRet[number] = toRet[number] + nombre
                    toRet[number]['name'] =  toRet[number]['name'] +nombre
                except:
                    pass
    else:
        toRet = {"Error":"Table no exist"}
    return toRet

@app.route('/',methods=['GET'])
def index():
    return render_template("index.html", ipPort=ipPort); 

@app.route('/search',methods=['POST'])
def search():
    table  = request.json['datos']
    cantRegsSelect = request.json['cantRegsSelect']
    try: 
        filtros = request.json['filters']
    except:
        filtros = ''
        pass
    
    thelistcommand = "SELECT "+table.upper()+" "

    for i,filtro in enumerate(filtros):
        thelistcommand += "WITH "+filtros[filtro]['1']+" "+filtros[filtro]['2']+' "'+filtros[filtro]['3']+'"'
        if (i != len(filtros) -1):
            thelistcommand += " AND "

    
    if (cantRegsSelect):
        thelistcommand += " SAMPLE "+cantRegsSelect
    resul = getSelectList( thelistcommand , ses)

    if len(resul) != 0:
        toRet = {
            "resul":resul
        }
    else:
        toRet = {
            "resul":"No se encontraron resultados"
        }
    
    return jsonify(toRet)

@app.route('/listDict/<table>',methods=['GET'])
def listDict(table):
    resul = getDict( table , ses)
    return jsonify(resul)

@app.route('/table/<table>/<id>',methods=['GET'])
def table(table,id):

    R = uopy.DynArray(session = getConnectionDB(ses))

    try:
        F = uopy.File(table.upper(),session = ses)
    except UOError as e:
        return ({"Error":str(e)})

    try:
        R = F.read(id).list
    except UOError as e:
        return ({"Error":str(e)})

    toRet = {}
    for i, elem in enumerate(R):
        if (type(elem) == str):
            toRet[i] = str(elem)
        elif (type(elem) == list):
            toRet[i] = ''
            for j,elemL2 in enumerate (elem):
                if (type(elemL2) == str):
                    try:
                        toRet[i][j] = str(elemL2)
                    except Exception as E:
                        toRet[i] = {j:str(elemL2)}
                elif (type(elemL2) == list):
                    toRet[i] = {j: ''}
                    for k,elemL3 in enumerate (elemL2):
                        if (type(elemL3) == str):
                            try:
                                toRet[i][j][k] = str(elemL3)
                            except Exception as E:
                                toRet[i][j] = {k:str(elemL3)}
                        elif (type(elemL3) == list):
                            toRet[i][j] = {k: ''}
                            for l,elemL4 in enumerate (elemL3):
                                if (type(elemL4) == str):
                                    try:
                                        toRet[i][j][k][l] = str(elemL4)
                                    except Exception as E:
                                        toRet[i][j][l] = {k:str(elemL4)}
    return jsonify(toRet)

@app.route('/editor/<table>/<id>',methods=['GET'])
def editor(table,id):

    R = uopy.DynArray(session = getConnectionDB(ses))

    try:
        F = uopy.File(table.upper(),session = ses)
    except UOError as e:
        return ({"Error":str(e)})

    try:
        R = F.read(id).list
    except UOError as e:
        return ({"Error":str(e)})

    data = {}
    countColumns = 1
    for i, elem in enumerate(R):
        if (type(elem) == str):
            data[i] = str(elem)
        elif (type(elem) == list):
            data[i] = ''
            for j,elemL2 in enumerate (elem):
                if (type(elemL2) == str):
                    try:
                        data[i][j+1] = str(elemL2)
                    except Exception as E:
                        data[i] = {j+1:str(elemL2)}
                elif (type(elemL2) == list):
                    countColumns = 2
                    try:
                        data[i][j+1] = ''
                    except:
                        data[i] = {}
                        data[i] = {j+1: ''}

                    for k,elemL3 in enumerate (elemL2):
                        if (type(elemL3) == str):
                            countColumns = 3
                            try:
                                data[i][j+1][k+1] = str(elemL3)
                            except Exception as E:
                                data[i][j+1] = {k+1:str(elemL3)}
                        elif (type(elemL3) == list):
                            countColumns = 3
                            data[i][j+1] = {k+1: ''}
                            for l,elemL4 in enumerate (elemL3):
                                if (type(elemL4) == str):
                                    try:
                                        data[i][j+1][k+1][l+1] = str(elemL4)
                                    except Exception as E:
                                        data[i][j+1][l+1] = {k+1:str(elemL4)}

    dic = getDict(table,ses)
    toRet = {}
    for key, value in dic.items():
        if (key > 0):
            try:
                toRet[key] = value
                toRet[key]['value']=[data[key-1]]
                if (toRet[key]['conversion'] != '' and data[key-1] != ''):
                    newData = {}
                    if (type(data[key-1]) == str):
                        toConv = data[key-1]
                        convertido=uopy.DynArray(toConv,session = getConnectionDB(ses)).oconv('D4/E').list[0]
                        newData[0] = str(convertido)
                    else:
                        for toConvKey, toConvValue in data[key-1].items():
                            toConv = toConvValue
                            convertido=uopy.DynArray(toConv,session = getConnectionDB(ses)).oconv('D4/E').list[0]
                            newData[toConvKey] = str(convertido)
                    toRet[key]['value'] = [newData]
            except Exception as e:
                toRet[key]['value']=['']

    return render_template("tableEdit.html", table =table, idRecord =id, data = toRet, colums = countColumns, ipPort=ipPort)

@app.route('/updateValue',methods=['POST'])
def updateValue():
    
    datos = request.json

    table = request.json['table'].upper()
    registro = request.json['registro']
    campo = request.json['campo'].upper()
    nuevoVal =request.json['nuevoVal']

    F = uopy.File(table,session = getConnectionDB(ses))

    F.write_named_fields([registro], [campo], [nuevoVal])

    return jsonify({"newValue":nuevoVal})

@app.route('/updateMValue',methods=['POST'])
def updateMValue():
    
    datos = request.json

    table = request.json['table'].upper()
    registro = request.json['registro']
    campo = request.json['campo'].upper()
    nuevoVal =request.json['nuevoVal']

    F = uopy.File(table,session = getConnectionDB(ses))
    
    if (type(nuevoVal) == str):
        try:
            F.write_named_fields([registro], [campo], [nuevoVal])
        except Exception as e:
            print("Error")
        toRet = nuevoVal
    else:
        toRet = {}
        toWrite = []
        for mvElem in nuevoVal:
            if (len(mvElem) == 1):
                toWrite.append(mvElem[0])
            else:
                toWrite.append(mvElem)
            try: 
                F.write_named_fields([registro], [campo], [[nuevoVal]])
            except Exception as e:
                print("Error")
        for i,elem in enumerate(nuevoVal):
            if (len(elem) == 1):
                toRet[i+1]=elem[0]
            else: 
                for j,elemL2 in enumerate(elem):
                    try:
                        toRet[i+1][j+1] = str(elemL2)
                    except Exception as E:
                        toRet[i+1] = {j+1:str(elemL2)}



    

    return ({"newValue":[str(toRet)]})

@app.route('/updateDataValue',methods=['POST'])
def updateDataValue():
    
    datos = request.json

    table = request.json['table'].upper()
    registro = int(request.json['registro'])
    campo = request.json['campo'].upper()
    nuevoVal =request.json['nuevoVal']

    F = uopy.File(table,session = getConnectionDB(ses))
    
    if (type(nuevoVal) == str):
        date_time_str = nuevoVal
        date_time_obj = datetime.strptime(date_time_str, '%d/%m/%y')

        try:
            F.write_named_fields([registro], [campo], [nuevoVal])
        except Exception as e:
            print("Error")
        toRet = nuevoVal
    else:
        toRet = {}
        toWrite = []
        grabar = 1
        for mvElem in nuevoVal:
            if (len(mvElem) == 1):
                dateTimeStr = mvElem[0]
                try:
                    dateTimeStr = str(datetime.strptime(dateTimeStr, '%d/%m/%Y'))
                except Exception as e:
                    grabar = 0
                toWrite.append(dateTimeStr)
            else:
                for toConvElem in mvElem:
                    try:
                        dateTimeStr = str(datetime.strptime(toConvElem, '%d/%m/%Y'))
                    except Exception as e:
                        grabar = 0
                toWrite.append(mvElem)

        if (grabar == 1):
            try: 
                F.write_named_fields([registro], [campo], [[nuevoVal]])
            except Exception as e:
                print("Error")
            for i,elem in enumerate(nuevoVal):
                if (len(elem) == 1):
                    toRet[i]=elem[0]
                else: 
                    for j,elemL2 in enumerate(elem):
                        try:
                            toRet[i][j] = str(elemL2)
                        except Exception as E:
                            toRet[i] = {j:str(elemL2)}

    return ({"newValue":[str(toRet)]})

if __name__ == "__main__":

    ses = getConnectionDB(ses)

    with open(os.getcwd()+"/config/config.json") as f:
        env_vars = json.loads(f.read())
        hostIP     = env_vars["hostIP"]
        puertoDev = env_vars["puertoDev"]
        ipPort = hostIP+":"+puertoDev

    app.run(host=hostIP,port=puertoDev,debug=True)    
