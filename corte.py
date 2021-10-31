import time
from pysnmp.hlapi import *
import time
import smtplib
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
def consultaSNMP(comunidad,host,oid):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad),
               UdpTransportTarget((host, 161)),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            varB=(' = '.join([x.prettyPrint() for x in varBind]))
            resultado= varB.split()[2]
            if((len(varB.split("Software")) > 1) | (resultado == 'Linux')):
                resultado = varB.split("=")[1]
    return resultado
def generarReporte(name,total,excedente,ordinaria,timeini,timefin):
    res = consultaSNMP('home','192.168.3.5',"1.3.6.1.2.1.1.1.0")
    if(len(res.split("Software")) > 1):
        sistema = res.split("Software")[1].split(" ")[1]
        version = res.split("Software")[1].split(" ")[3]
    else:
        sistema = res.split(" ")[1]
        version = res.split(" ")[3]
    ubicacion = consultaSNMP('home','192.168.3.5',"1.3.6.1.2.1.1.6.0")
    tiempo = consultaSNMP('home','192.168.3.5',"1.3.6.1.2.1.1.3.0")
    tiempo ="{0:.2f}".format(((int(tiempo)*0.01)/60)/60)
    ip = '192.168.3.5'
    c = canvas.Canvas("reportes/"+name+".pdf",pagesize=A4)
    w, h = A4
    if(sistema == "Linux"):
        c.drawImage("IMG/linux.jpg",10,h-60,width=50,height=50)
    else:
        c.drawImage("IMG/windows.jpeg",10,h-60,width=50,height=50)
    c.setFont("Helvetica", 10)
    c.drawString(65, h-25, "SO: "+sistema+"  Version: "+version+"  Ubicacion: "+ubicacion)
    c.drawString(65, h-50, "Tiempo de actividad antes del ultimo reinicio: "+tiempo+"hrs  Comunidad: "+'home'+' IP: '+ip)
    c.line(0,h-65,w,h-65)
    c.drawString(65,h-85,"Fecha de inicio: "+timeini+"     Fecha de corte: " +timefin)
    c.drawString(65,h-100,"Total: $"+str(total)+"     Se excedio la tarifa normal por: " +str(excedente)+" paquetes")
    c.drawString(65,h-115,"Total tarifa ordinaria: $"+str(ordinaria)+"     Total excedido: $" +str((excedente/1000)*(tarifa*2)))

    c.save()
tarifa = 10
maximo = 20000
print("Ingresa la fecha y hora de inicio (DD-MM-AAAA HH:MM)")
timeini = input()
timeinistr = timeini
timeini =int(time.mktime(time.strptime(timeini,"%d-%m-%Y %H:%M")))
print("Ingresa la fecha y hora de termino ((DD-MM-AAAA HH:MM)")
timefin = input()
timefinstr = timefin
timefin =int(time.mktime(time.strptime(timefin,"%d-%m-%Y %H:%M")))

f = open("bd/bd.txt","r")
lines = f.readlines()
splited = []
ini = 'x'
fin = 'x'
iniFlag = True
for line in lines:
    split = line.split(" ")
    split[3] = split[3][0:len(split[3])-1]
    if(iniFlag):
        if(timeini <= int(split[3])):
            ini = split[1]
            iniFlag = False
    if(timefin <= int(split[3])):
        fin = split[1]
        break

    splited.append(split)
if(ini == 'x' or fin == 'x'):
    print("Error al buscar en los datos")
    exit()
consumido = int(fin) - int(ini)
if(consumido < maximo):
    excedente = 0
    total = tarifa * (consumido/1000)
    ordinaria = total
else:
    excedente = consumido-maximo
    ordinaria = (tarifa * (maximo/1000)) 
    total = ordinaria + ((tarifa*2)*((consumido-maximo)/1000))
    
generarReporte("consumo",total,excedente,ordinaria,timeinistr,timefinstr)
print(total)
print(excedente)
