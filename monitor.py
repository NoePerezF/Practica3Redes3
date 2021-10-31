from pysnmp.hlapi import *
import time
import smtplib
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
imgpath = 'IMG/'
fname = 'bd.txt'

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



while(1):
    bd = open('bd/'+fname,'a')
    data = "UDP: "+consultaSNMP('home','192.168.3.5','1.3.6.1.2.1.7.1.0') + " time: " +str(int(time.time()))+'\n'
    print(data)
    bd.write(data)
    bd.close()
    time.sleep(10)