#Imports de la aplicacion actual
from flask import Flask, request, Blueprint,jsonify, render_template,session
import json
import uopy
from uopy import UOError , Command, List
from uopy import EXEC_MORE_OUTPUT

#Imports del sistema
import os

#Imports de secciones
from database import getConnectionDB

app = Flask(__name__)

ses = ""

def getSelectList( thelistcommand, session):
    
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

@app.route('/listar/<table>',methods=['GET'])
def listar(table):
    thelistcommand = "SELECT "+table
    resul = getSelectList( thelistcommand , ses)

    return render_template("listar.html", resul = resul, table = table); 

@app.route('/',methods=['GET'])
def index():
    return render_template("index.html"); 

@app.route('/search',methods=['POST'])
def search():
    ses = getConnectionDB()
    table  = request.json['datos']
    thelistcommand = "SELECT "+table
    resul = getSelectList( thelistcommand , ses)

    toRet = {
        "resul":resul
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
                        data[i][j] = str(elemL2)
                    except Exception as E:
                        data[i] = {j:str(elemL2)}
                elif (type(elemL2) == list):
                    countColumns = 2
                    data[i][j] = ''
                    for k,elemL3 in enumerate (elemL2):
                        if (type(elemL3) == str):
                            try:
                                data[i][j][k] = str(elemL3)
                            except Exception as E:
                                data[i][j] = {k:str(elemL3)}
                        elif (type(elemL3) == list):
                            countColums = 3
                            data[i][j] = {k: ''}
                            for l,elemL4 in enumerate (elemL3):
                                if (type(elemL4) == str):
                                    try:
                                        data[i][j][k][l] = str(elemL4)
                                    except Exception as E:
                                        data[i][j][l] = {k:str(elemL4)}

    dic = getDict(table,ses)
    toRet = {}
    for key, value in dic.items():
        if (key > 0):
            try:
                toRet[key] = value
                toRet[key]['value']=[data[key-1]]

            except:
                toRet[key]['value']=['']

    return render_template("tableEdit.html", table =table, idRecord =id, data = toRet, colums = countColumns)
    

def getText(arr):
    if (type(arr) == str):
        return arr
    elif (type(arr[0]) == str):
        toRet = '\n'.join(arr)
        return toRet
    else:
        return getText(arr[0])

def getTextV2(arr):
    if (type(arr) == str):
        return arr
    elif (type(arr[0]) == str):
        return arr[0]
    elif (type(arr[0][0]) == str):
        return arr[0][0]
    elif (type(arr[0][0][0]) == str):
        toRet = '\n'.join(arr[0][0])
        return toRet
    else:
        return str(arr)

@app.route('/preview',methods=['POST'])
def preview():
    datos = request.json['datos']
    idRecord = request.json['idRecord']
    nameFile = "static/TEXTOS_MAILS_"+str(idRecord)+".html"

    f2 = open(nameFile, "w")
    f2.write(datos)
    f2.close()

    nombre = {
        "nombre":nameFile
    }
    return jsonify(nombre)

@app.route('/updateValue',methods=['POST'])
def updateValue():
    
    datos = request.json

    table = request.json['table'].upper()
    registro = int(request.json['registro'])
    campo = request.json['campo'].upper()
    nuevoVal =request.json['nuevoVal']

    F = uopy.File(table,session = getConnectionDB(ses))

    F.write_named_fields([registro], [campo], [nuevoVal])

    return jsonify({"newValue":nuevoVal})

@app.route('/updateMValue',methods=['POST'])
def updateMValue():
    
    datos = request.json

    table = request.json['table'].upper()
    registro = int(request.json['registro'])
    campo = request.json['campo'].upper()
    nuevoVal =request.json['nuevoVal']

    F = uopy.File(table,session = getConnectionDB(ses))
    
    if (type(nuevoVal) == str):
        F.write_named_fields([registro], [campo], [nuevoVal])
        toRet = nuevoVal
    else:
        toRet = {}
        toWrite = []
        for mvElem in nuevoVal:
            if (len(mvElem) == 1):
                toWrite.append(mvElem[0])
            else:
                toWrite.append(mvElem)
        F.write_named_fields([registro], [campo], [[nuevoVal]])
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

    app.run(host=hostIP,port=puertoDev,debug=True)    
