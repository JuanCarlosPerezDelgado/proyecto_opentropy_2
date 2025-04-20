from datetime import datetime, timedelta         
import pandas as pd
import matplotlib.pyplot as plt     
import numpy as np
import streamlit as st
import altair as alt
from time import sleep
import streamlit_option_menu
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
import CoolProp.CoolProp as CP
from scipy.optimize import minimize_scalar
from scipy.optimize import minimize

def busqueda_puntos_compresor(puntos_compresor,df_analizador_redes_ensayo,df_equipo_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo):
    puntos_encontrados=list()
    for i,(indice,valor) in enumerate(df_equipo_ensayo['Rele compresor (on/off)'].items()):

        if i<(len(df_equipo_ensayo['Rele compresor (on/off)'])-1):
            if valor!=0 and df_equipo_ensayo.iloc[i+1,df_equipo_ensayo.columns.get_loc('Rele compresor (on/off)')]==0:
                valido=True
                for j in range(1,puntos_compresor):
                    if i - j < 0 or df_equipo_ensayo.iloc[i-j,df_equipo_ensayo.columns.get_loc('Rele compresor (on/off)')]==0:
                        valido=False
                        break
                if valido==True:
                    puntos_encontrados.append(indice)

        elif i == (len(df_equipo_ensayo['Rele compresor (on/off)'])-1) and valor==1:
            valido=True
            for j in range(1,puntos_compresor):
                if i - j < 0 or df_equipo_ensayo.iloc[i-j,df_equipo_ensayo.columns.get_loc('Rele compresor (on/off)')]==0:
                        valido=False
                        break
            if valido==True:
                    puntos_encontrados.append(indice)

    lista_estacionarios=list()
    for i,fecha_fin in enumerate(puntos_encontrados):
        if puntos_compresor>1:
            fecha_inicio=fecha_fin-timedelta(minutes=(puntos_compresor-1))
        else:
            fecha_inicio=fecha_fin
        lista_estacionarios.append(f'Cusi-estacionario {i+1} - Desde {fecha_inicio.strftime('%H:%M')} hasta {fecha_fin.strftime('%H:%M')}')

    return lista_estacionarios,puntos_encontrados

def busqueda_puntos_variable(variable_banda,consigna,banda_superior,banda_inferior,df_analizador_redes_ensayo,df_equipo_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo):
    df_ampliado_variable=pd.concat([df_equipo_ensayo,df_analizador_redes_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo],axis=1)

    def funcion(df_ampliado_variable):
        if (consigna-banda_inferior)<=df_ampliado_variable[variable_banda]<=(consigna+banda_superior):
            valor=1
        else:
            valor=0
        return valor

    df_ampliado_variable.loc[:,'Condicion']=df_ampliado_variable.apply(funcion,axis=1)
        
    puntos_encontrados_variable=list()
    duracion=1
    contador=0
    inicio=None
    indice_anterior=None
    for i, (indice,valor) in enumerate(df_ampliado_variable.loc[:,'Condicion'].items()):
        if valor==1:
            if contador==0:
                inicio=indice
            contador +=1
            indice_anterior=indice
        else:
            if contador >= duracion:
                puntos_encontrados_variable.append((inicio,indice_anterior))
            contador=0
    if contador >= duracion:
        puntos_encontrados_variable.append((inicio, df_ampliado_variable.index[-1]))

    lista_estacionarios_variable=list()
    for i, (inicio, fin) in enumerate(puntos_encontrados_variable):
        duracion=((fin - inicio).total_seconds() / 60)+1
        lista_estacionarios_variable.append(f'Cuasi-estacionario {i+1} - Desde {inicio} hasta {fin} - Duración {duracion} min')

    return lista_estacionarios_variable,puntos_encontrados_variable


def busqueda_puntos_control(consigna_temperatura_camara,banda_superior_temperatura_camara,banda_inferior_temperatura_camara,consigna_temperatura,banda_superior_temperatura,banda_inferior_temperatura,subrenfriamiento,sobrecalentamiento,apertura_valvula,df_analizador_redes_ensayo,df_equipo_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo):

    df_ampliado_control=pd.concat([df_equipo_ensayo,df_analizador_redes_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo],axis=1)

    def funcion_1(df_ampliado_control):
        if ((consigna_temperatura_camara-banda_inferior_temperatura_camara)<=((df_ampliado_control['Temperatura camara (evaporador 1) (°C)']+df_ampliado_control['Temperatura camara (evaporador 2) (°C)'])/2)<=(consigna_temperatura_camara+banda_superior_temperatura_camara)) and ((consigna_temperatura-banda_inferior_temperatura)<=df_ampliado_control['Temperatura evaporacion (°C)']<=(consigna_temperatura+banda_superior_temperatura)) and (abs(df_ampliado_control['Temperatura salida gas cooler (°C)']-df_ampliado_control['Temperatura exterior (°C)'])<=subrenfriamiento) and ((((df_ampliado_control['Recalentamiento (valvula expansion 1) (K)']+df_ampliado_control['Recalentamiento (valvula expansion 2) (K)'])/2))<=sobrecalentamiento) and (df_ampliado_control['Apertura valvula by-pass (%)']<=apertura_valvula):
            valor=1
        else:
            valor=0
        return valor            
    def funcion_2(df_ampliado_control):
        if ((consigna_temperatura_camara-banda_inferior_temperatura_camara)<=((df_ampliado_control['Temperatura camara (evaporador 1) (°C)']+df_ampliado_control['Temperatura camara (evaporador 2) (°C)'])/2)<=(consigna_temperatura_camara+banda_superior_temperatura_camara)) and ((consigna_temperatura-banda_inferior_temperatura)<=df_ampliado_control['Temperatura evaporacion (°C)']<=(consigna_temperatura+banda_superior_temperatura)) and (abs(df_ampliado_control['Temperatura salida gas cooler (°C)']-df_ampliado_control['Temperatura exterior (°C)'])<=subrenfriamiento) and ((((df_ampliado_control['Temperatura aspiracion (valvula expansion 1) (°C)']+df_ampliado_control['Temperatura aspiracion (valvula expansion 2) (°C)'])/2)-df_ampliado_control['Temperatura evaporacion (°C)'])<=sobrecalentamiento) and (df_ampliado_control['Apertura valvula by-pass (%)']<=apertura_valvula):
            valor=1
        else:
            valor=0
        return valor
    def funcion_3(df_ampliado_control):
        if ((consigna_temperatura_camara-banda_inferior_temperatura_camara)<=((df_ampliado_control['Temperatura camara (evaporador 1) (°C)']+df_ampliado_control['Temperatura camara (evaporador 2) (°C)'])/2)<=(consigna_temperatura_camara+banda_superior_temperatura_camara)) and ((consigna_temperatura-banda_inferior_temperatura)<=df_ampliado_control['Temperatura evaporacion (°C)']<=(consigna_temperatura+banda_superior_temperatura)) and (abs(df_ampliado_control['Temperatura salida gas cooler (°C)']-df_ampliado_control['Temperatura exterior (°C)'])<=subrenfriamiento) and ((df_ampliado_control['Temperatura aspiracion (°C)']-df_ampliado_control['Temperatura evaporacion (°C)'])<=sobrecalentamiento) and (df_ampliado_control['Apertura valvula by-pass (%)']<=apertura_valvula):
            valor=1
        else:
            valor=0
        return valor  
        

    if 'Recalentamiento (valvula expansion 1) (K)' in df_ampliado_control.columns:
        df_ampliado_control.loc[:,'Condicion']=df_ampliado_control.apply(funcion_1,axis=1)
    elif 'Recalentamiento (valvula expansion 1) (K)' not in df_ampliado_control.columns and 'Temperatura aspiracion (valvula expansion 1) (°C)' in df_ampliado_control.columns:
        df_ampliado_control.loc[:,'Condicion']=df_ampliado_control.apply(funcion_2,axis=1)
    else: 
        df_ampliado_control.loc[:,'Condicion']=df_ampliado_control.apply(funcion_3,axis=1)

    puntos_encontrados_control=list()
    duracion=1
    contador=0
    inicio=None
    indice_anterior=None
    for i, (indice,valor) in enumerate(df_ampliado_control.loc[:,'Condicion'].items()):
        if valor==1:
            if contador==0:
                inicio=indice
            contador +=1
            indice_anterior=indice
        else:
            if contador >= duracion:
                puntos_encontrados_control.append((inicio,indice_anterior))
            contador=0
    if contador >= duracion:
        puntos_encontrados_control.append((inicio, df_ampliado_control.index[-1]))

    lista_estacionarios_control=list()
    for i, (inicio, fin) in enumerate(puntos_encontrados_control):
        duracion=((fin - inicio).total_seconds() / 60)+1
        lista_estacionarios_control.append(f'Cuasi-estacionario {i+1} - Desde {inicio} hasta {fin} - Duración {duracion} min')

    return lista_estacionarios_control,puntos_encontrados_control

def calculos_termodinamicos(eleccion,lista,puntos,df_analizador_redes_ensayo,df_equipo_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo):
    #Intervalo de tiempo del ensayo seleccionado
    info_estacionario=lista.index(eleccion)
    inicio,fin=puntos[info_estacionario]

    #Generación de subdataframe en función del ensayo elegido
    df_analizador_redes_estacionario=df_analizador_redes_ensayo.loc[inicio:fin,:]
    df_equipo_estacionario=df_equipo_ensayo.loc[inicio:fin,:]
    df_evaporador_04_estacionario=df_evaporador_04_ensayo.loc[inicio:fin,:]
    df_valvula_expansion_05_estacionario=df_valvula_expansion_05_ensayo.loc[inicio:fin,:]
    df_evaporador_06_estacionario=df_evaporador_06_ensayo.loc[inicio:fin,:]
    df_valvula_expansion_07_estacionario=df_valvula_expansion_07_ensayo.loc[inicio:fin,:]
    df_ampliado=pd.concat([df_analizador_redes_estacionario,df_equipo_estacionario,df_evaporador_04_estacionario,df_valvula_expansion_05_estacionario,df_evaporador_06_estacionario,df_valvula_expansion_07_estacionario],axis=1)

    media=df_ampliado.mean()
  
    tabla_propiedades=pd.DataFrame(columns=['Temperatura (°C)','Presión (bar)','Entalpía (kJ/Kg)','Entropía (kJ/Kg·K)','Título de vapor','Densidad (Kg/m^3)','Caudal másico (Kg/s)'],index=['1','2','3','4s','4','5','6s','6','7','8','9','10','11','12','13','14'])
    
    #Punto 1
    if ('Presion de baja (valvula expansion 1) (bar)' in media.index) and ('Presion de baja (valvula expansion 2) (bar)' in media.index):
        presion_evaporacion=(media['Presion evaporacion (bar)']+media['Presion de baja (valvula expansion 1) (bar)']+media['Presion de baja (valvula expansion 2) (bar)'])/3
    else:
        presion_evaporacion=media['Presion evaporacion (bar)']
    tabla_propiedades.loc['1','Temperatura (°C)']=(CP.PropsSI("T", "P", presion_evaporacion*(10**5), "Q",1 , "CO2"))-273.15 #Temperatura de evaporación
    tabla_propiedades.loc['1','Presión (bar)']=presion_evaporacion
    tabla_propiedades.loc['1','Título de vapor']=1.000
    tabla_propiedades.loc['1','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P", presion_evaporacion*(10**5), "Q",1 , "CO2"))/1000
    tabla_propiedades.loc['1','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",presion_evaporacion*(10**5) , "Q", 1, "CO2"))/1000
    tabla_propiedades.loc['1','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",presion_evaporacion*(10**5) , "Q", 1, "CO2")

    #Punto 2
    if ('Recalentamiento (valvula expansion 1) (K)' in media.index) and ('Recalentamiento (valvula expansion 2) (K)' in media.index):
        tabla_propiedades.loc['2','Temperatura (°C)']=(CP.PropsSI("T", "P", presion_evaporacion*(10**5), "Q",1 , "CO2"))-273.15+abs((media['Recalentamiento (valvula expansion 1) (K)']+media['Recalentamiento (valvula expansion 2) (K)'])/2)
        tabla_propiedades.loc['2','Temperatura (°C)']=(tabla_propiedades.loc['2','Temperatura (°C)']+media['Temperatura aspiracion (°C)'])/2 
        temperatura_sobrecalentado=tabla_propiedades.loc['2','Temperatura (°C)']
    elif ('Temperatura aspiracion (valvula expansion 1) (°C)' in media.index) and ('Temperatura aspiracion (valvula expansion 2) (°C)' in media.index):
        tabla_propiedades.loc['2','Temperatura (°C)']=(media['Temperatura aspiracion (valvula expansion 1) (°C)']+media['Temperatura aspiracion (valvula expansion 2) (°C)']+media['Temperatura aspiracion (°C)'])/3 
        temperatura_sobrecalentado=tabla_propiedades.loc['2','Temperatura (°C)']
    else:
        tabla_propiedades.loc['2','Temperatura (°C)']=media['Temperatura aspiracion (°C)']
        temperatura_sobrecalentado=tabla_propiedades.loc['2','Temperatura (°C)']
    tabla_propiedades.loc['2','Presión (bar)']=presion_evaporacion
    tabla_propiedades.loc['2','Título de vapor']=None
    tabla_propiedades.loc['2','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P", presion_evaporacion*(10**5), "T",temperatura_sobrecalentado+273.15 , "CO2"))/1000
    tabla_propiedades.loc['2','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",presion_evaporacion*(10**5) , "T", temperatura_sobrecalentado+273.15, "CO2"))/1000
    tabla_propiedades.loc['2','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",presion_evaporacion*(10**5) , "T", temperatura_sobrecalentado+273.15, "CO2")

    #Punto 6
    tabla_propiedades.loc['6','Temperatura (°C)']=media['Temperatura descarga (°C)']
    tabla_propiedades.loc['6','Presión (bar)']=media['Presion condensacion (bar)']
    tabla_propiedades.loc['6','Título de vapor']=None
    tabla_propiedades.loc['6','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P", media['Presion condensacion (bar)']*(10**5), "T",media['Temperatura descarga (°C)']+273.15 , "CO2"))/1000
    tabla_propiedades.loc['6','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media['Presion condensacion (bar)']*(10**5) , "T", media['Temperatura descarga (°C)']+273.15, "CO2"))/1000
    tabla_propiedades.loc['6','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion condensacion (bar)']*(10**5) , "T", media['Temperatura descarga (°C)']+273.15, "CO2")    

    #Punto 7
    tabla_propiedades.loc['7','Temperatura (°C)']=media['Temperatura salida gas cooler (°C)']
    tabla_propiedades.loc['7','Presión (bar)']=media['Presion condensacion (bar)'] 
    tabla_propiedades.loc['7','Título de vapor']=None
    tabla_propiedades.loc['7','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P", media['Presion condensacion (bar)']*(10**5), "T",media['Temperatura salida gas cooler (°C)']+273.15 , "CO2"))/1000
    tabla_propiedades.loc['7','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media['Presion condensacion (bar)']*(10**5) , "T", media['Temperatura salida gas cooler (°C)']+273.15, "CO2"))/1000
    tabla_propiedades.loc['7','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion condensacion (bar)']*(10**5) , "T", media['Temperatura salida gas cooler (°C)']+273.15, "CO2")           
    
    #Punto 8
    tabla_propiedades.loc['8','Presión (bar)']=media['Presion deposito (bar)'] 
    tabla_propiedades.loc['8','Entalpía (kJ/Kg)']=tabla_propiedades.loc['7','Entalpía (kJ/Kg)']
    tabla_propiedades.loc['8','Título de vapor']=CP.PropsSI("Q", "P",media['Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2")
    tabla_propiedades.loc['8','Temperatura (°C)']=(CP.PropsSI("T", "P",media['Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2"))-273.15
    tabla_propiedades.loc['8','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2")
    tabla_propiedades.loc['8','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media['Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
    tabla_propiedades.loc['8','Título de vapor']=round(tabla_propiedades.loc['8','Título de vapor'],3)

    #Punto 9
    tabla_propiedades.loc['9','Presión (bar)']=media['Presion deposito (bar)'] 
    tabla_propiedades.loc['9','Título de vapor']=0.000
    tabla_propiedades.loc['9','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media['Presion deposito (bar)']*(10**5) , "Q",0, "CO2"))/1000
    tabla_propiedades.loc['9','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media['Presion deposito (bar)']*(10**5) , "Q",0, "CO2"))/1000
    tabla_propiedades.loc['9','Temperatura (°C)']=(CP.PropsSI("T", "P",media['Presion deposito (bar)']*(10**5) , "Q",0, "CO2"))-273.15
    tabla_propiedades.loc['9','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion deposito (bar)']*(10**5) , "Q", 0, "CO2")

    #Punto 10
    tabla_propiedades.loc['10','Entalpía (kJ/Kg)']=tabla_propiedades.loc['9','Entalpía (kJ/Kg)']
    tabla_propiedades.loc['10','Presión (bar)']=presion_evaporacion
    tabla_propiedades.loc['10','Título de vapor']=CP.PropsSI("Q", "P",presion_evaporacion*(10**5) , "H", tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2")
    tabla_propiedades.loc['10','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",presion_evaporacion*(10**5) , "H",tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
    tabla_propiedades.loc['10','Temperatura (°C)']=tabla_propiedades.loc['1','Temperatura (°C)']
    tabla_propiedades.loc['10','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",presion_evaporacion*(10**5) , "H", tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2")
    tabla_propiedades.loc['10','Título de vapor']=round(tabla_propiedades.loc['10','Título de vapor'],3)

    #Punto 11
    tabla_propiedades.loc['11','Presión (bar)']=media['Presion deposito (bar)'] 
    tabla_propiedades.loc['11','Título de vapor']=1.000
    tabla_propiedades.loc['11','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media['Presion deposito (bar)']*(10**5) , "Q",1, "CO2"))/1000
    tabla_propiedades.loc['11','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media['Presion deposito (bar)']*(10**5) , "Q",1, "CO2"))/1000
    tabla_propiedades.loc['11','Temperatura (°C)']=(CP.PropsSI("T", "P",media['Presion deposito (bar)']*(10**5) , "Q",1, "CO2"))-273.15
    tabla_propiedades.loc['11','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion deposito (bar)']*(10**5) , "Q", 1, "CO2")

    #Punto 12
    tabla_propiedades.loc['12','Presión (bar)']=tabla_propiedades.loc['11','Presión (bar)']
    tabla_propiedades.loc['12','Entalpía (kJ/Kg)']=tabla_propiedades.loc['11','Entalpía (kJ/Kg)']
    tabla_propiedades.loc['12','Temperatura (°C)']=tabla_propiedades.loc['11','Temperatura (°C)']
    tabla_propiedades.loc['12','Título de vapor']=tabla_propiedades.loc['11','Título de vapor']
    tabla_propiedades.loc['12','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['11','Entropía (kJ/Kg·K)']
    tabla_propiedades.loc['12','Densidad (Kg/m^3)']=tabla_propiedades.loc['11','Densidad (Kg/m^3)']

    #Punto 13
    tabla_propiedades.loc['13','Presión (bar)']=presion_evaporacion
    tabla_propiedades.loc['13','Entalpía (kJ/Kg)']=tabla_propiedades.loc['12','Entalpía (kJ/Kg)']
    tabla_propiedades.loc['13','Temperatura (°C)']=tabla_propiedades.loc['1','Temperatura (°C)']
    tabla_propiedades.loc['13','Título de vapor']=CP.PropsSI("Q", "P",presion_evaporacion*(10**5) , "H", tabla_propiedades.loc['12','Entalpía (kJ/Kg)']*1000, "CO2")
    tabla_propiedades.loc['13','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",presion_evaporacion*(10**5) , "H",tabla_propiedades.loc['12','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
    tabla_propiedades.loc['13','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",presion_evaporacion*(10**5) , "H", tabla_propiedades.loc['12','Entalpía (kJ/Kg)']*1000, "CO2")
    tabla_propiedades.loc['13','Título de vapor']=round(tabla_propiedades.loc['13','Título de vapor'],3)

    #Punto 14
    tabla_propiedades.loc['14','Presión (bar)']=tabla_propiedades.loc['11','Presión (bar)']
    tabla_propiedades.loc['14','Entalpía (kJ/Kg)']=tabla_propiedades.loc['11','Entalpía (kJ/Kg)']
    tabla_propiedades.loc['14','Temperatura (°C)']=tabla_propiedades.loc['11','Temperatura (°C)']
    tabla_propiedades.loc['14','Título de vapor']=tabla_propiedades.loc['11','Título de vapor']
    tabla_propiedades.loc['14','Entalpía (kJ/Kg)']=tabla_propiedades.loc['11','Entalpía (kJ/Kg)']
    tabla_propiedades.loc['14','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['11','Entropía (kJ/Kg·K)']
    tabla_propiedades.loc['14','Densidad (Kg/m^3)']=tabla_propiedades.loc['11','Densidad (Kg/m^3)']

    if media['Potencia compresor (%)']>50:
       F=1.6*media['Potencia compresor (%)']/2
    else:
       F=80/2

    R_volumetrico_baja_teorico=16.6771332-0.01201859*media['Presion condensacion (bar)']-0.24571796*presion_evaporacion+3.20332109*F-0.00191565*media['Presion condensacion (bar)']**2-0.00219801*(presion_evaporacion**2)-0.02935512*(F**2)+0.00394487*media['Presion condensacion (bar)']*presion_evaporacion-0.00015889*media['Presion condensacion (bar)']*F+0.00468126*presion_evaporacion*F
    R_volumetrico_alta_teorico=(16.6771332-0.01201859*media['Presion condensacion (bar)']-0.24571796*presion_evaporacion+3.20332109*F-0.00191565*media['Presion condensacion (bar)']**2-0.00219801*(presion_evaporacion**2)-0.02935512*(F**2)+0.00394487*media['Presion condensacion (bar)']*presion_evaporacion-0.00015889*media['Presion condensacion (bar)']*F+0.00468126*presion_evaporacion*F)*(5.6/8)
    R_isentropico=20.4779885-0.08736845*tabla_propiedades.loc['6','Presión (bar)']+1.02075047*presion_evaporacion+1.6838928*F-0.00394391*(tabla_propiedades.loc['6','Presión (bar)']**2)-0.03363405*(presion_evaporacion**2)-0.01626644*(F**2)+0.01909573*tabla_propiedades.loc['6','Presión (bar)']*presion_evaporacion+0.00315153*tabla_propiedades.loc['6','Presión (bar)']*F-0.01128725*presion_evaporacion*F 
    
    #R_volumetrico_baja_teorico=(1.30455467+0.00970194263*presion_evaporacion-0.0996564037*(media['Presion condensacion (bar)']/presion_evaporacion))*100
    #R_volumetrico_alta_teorico=(1.09386887+0.000763078811*media['Presion deposito (bar)']-0.0876745754*(media['Presion condensacion (bar)']/presion_evaporacion))*100
    #R_isentropico=(0.707934084+0.0301499917*presion_evaporacion-0.0596514832*(media['Presion condensacion (bar)']/presion_evaporacion))*100

    #print('Juan Carlos')
    #R_volumetrico_baja_teorico2=16.6771332-0.01201859*media['Presion condensacion (bar)']-0.24571796*presion_evaporacion+3.20332109*F-0.00191565*media['Presion condensacion (bar)']**2-0.00219801*(presion_evaporacion**2)-0.02935512*(F**2)+0.00394487*media['Presion condensacion (bar)']*presion_evaporacion-0.00015889*media['Presion condensacion (bar)']*F+0.00468126*presion_evaporacion*F
    #R_volumetrico_alta_teorico2=(16.6771332-0.01201859*media['Presion condensacion (bar)']-0.24571796*presion_evaporacion+3.20332109*F-0.00191565*media['Presion condensacion (bar)']**2-0.00219801*(presion_evaporacion**2)-0.02935512*(F**2)+0.00394487*media['Presion condensacion (bar)']*presion_evaporacion-0.00015889*media['Presion condensacion (bar)']*F+0.00468126*presion_evaporacion*F)*(5.6/8)
    #R_isentropico2=20.4779885-0.08736845*tabla_propiedades.loc['6','Presión (bar)']+1.02075047*presion_evaporacion+1.6838928*F-0.00394391*(tabla_propiedades.loc['6','Presión (bar)']**2)-0.03363405*(presion_evaporacion**2)-0.01626644*(F**2)+0.01909573*tabla_propiedades.loc['6','Presión (bar)']*presion_evaporacion+0.00315153*tabla_propiedades.loc['6','Presión (bar)']*F-0.01128725*presion_evaporacion*F 
    #print(R_volumetrico_baja_teorico2)
    #print(R_volumetrico_alta_teorico2)
    #print(R_isentropico2)

    #R_volumetrico_baja_teorico3=(1.30455467+0.00970194263*presion_evaporacion-0.0996564037*(media['Presion condensacion (bar)']/presion_evaporacion))*100
    #R_volumetrico_alta_teorico3=(1.09386887+0.000763078811*media['Presion deposito (bar)']-0.0876745754*(media['Presion condensacion (bar)']/presion_evaporacion))*100
    #R_isentropico3=(0.707934084+0.0301499917*presion_evaporacion-0.0596514832*(media['Presion condensacion (bar)']/presion_evaporacion))*100
    #print('Miguel')
    #print(R_volumetrico_baja_teorico3)
    #print(R_volumetrico_alta_teorico3)
    #print(R_isentropico3)
    if media['Apertura valvula by-pass (%)']==0:
        def calcular(variables):
            m_3,m_5=variables

            tabla_propiedades.loc['3','Caudal másico (Kg/s)']=m_3
            tabla_propiedades.loc['5','Caudal másico (Kg/s)']=m_5
            tabla_propiedades.loc['3','Densidad (Kg/m^3)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']/((8*(R_volumetrico_baja_teorico/100)*F)/10**6)
            tabla_propiedades.loc['5','Densidad (Kg/m^3)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']/((5.6*(R_volumetrico_alta_teorico/100)*F)/10**6)

            tabla_propiedades.loc['3','Presión (bar)']=presion_evaporacion
            tabla_propiedades.loc['3','Temperatura (°C)']=(CP.PropsSI("T", "P",presion_evaporacion*(10**5) , "D", tabla_propiedades.loc['3','Densidad (Kg/m^3)'], "CO2"))-273.15
            tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",presion_evaporacion*(10**5) , "D", tabla_propiedades.loc['3','Densidad (Kg/m^3)'], "CO2"))/1000
            tabla_propiedades.loc['3','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",presion_evaporacion*(10**5) , "D",tabla_propiedades.loc['3','Densidad (Kg/m^3)'], "CO2"))/1000

            tabla_propiedades.loc['5','Presión (bar)']=media['Presion deposito (bar)']
            tabla_propiedades.loc['5','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))-273.15
            tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000
            tabla_propiedades.loc['5','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D",tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000

            tabla_propiedades.loc['4s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']
            tabla_propiedades.loc['4s','Presión (bar)']=media['Presion deposito (bar)']
            tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media['Presion deposito (bar)']*(10**5) , "S",tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
            tabla_propiedades.loc['4s','Temperatura (°C)']=(CP.PropsSI("T", "P",media['Presion deposito (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
            tabla_propiedades.loc['4s','Caudal másico (Kg/s)']=0
            tabla_propiedades.loc['4s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion deposito (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2")

            tabla_propiedades.loc['6s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']
            tabla_propiedades.loc['6s','Presión (bar)']=media['Presion condensacion (bar)']
            tabla_propiedades.loc['6s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media['Presion condensacion (bar)']*(10**5) , "S",tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
            tabla_propiedades.loc['6s','Temperatura (°C)']=(CP.PropsSI("T", "P",media['Presion condensacion (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
            tabla_propiedades.loc['6s','Caudal másico (Kg/s)']=0
            tabla_propiedades.loc['6s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion condensacion (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2")

            tabla_propiedades.loc['4','Entalpía (kJ/Kg)']=tabla_propiedades.loc['3','Entalpía (kJ/Kg)']+(tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])/(R_isentropico/100)
            tabla_propiedades.loc['4','Presión (bar)']=media['Presion deposito (bar)']
            tabla_propiedades.loc['4','Temperatura (°C)']=(CP.PropsSI("T", "P",media['Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))-273.15
            tabla_propiedades.loc['4','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2")
            tabla_propiedades.loc['4','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
            tabla_propiedades.loc['4','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media['Presion deposito (bar)']*(10**5) , "H",tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))/1000

            H_6=tabla_propiedades.loc['5','Entalpía (kJ/Kg)']+(tabla_propiedades.loc['6s','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])/(R_isentropico/100)
            H_3=tabla_propiedades.loc['3','Entalpía (kJ/Kg)']

            m_14=m_5-m_3
            error_caudal=abs(m_14-m_5*tabla_propiedades.loc['8','Título de vapor'])
            error_punto_6=abs(H_6-tabla_propiedades.loc['6','Entalpía (kJ/Kg)'])
            error_punto_3=abs(H_3-tabla_propiedades.loc['2','Entalpía (kJ/Kg)'])

        #Combinación de objetivos (método de suma ponderada)
            peso_caudal = 0.3  
            peso_punto_6 = 0.4  
            peso_punto_3=0.3
            return peso_caudal*error_caudal+peso_punto_6*error_punto_6+peso_punto_3*error_punto_3

        resultado = minimize(calcular,
        x0=[0.01, 0.015],
        bounds=[(0.005, 0.025), (0.01, 0.03)],
        method='L-BFGS-B',
        options={'ftol': 1e-4}
        )
    
        tabla_propiedades.loc['4','Título de vapor']=None
        tabla_propiedades.loc['3','Título de vapor']=None
        tabla_propiedades.loc['4s','Título de vapor']=None
        tabla_propiedades.loc['5','Título de vapor']=None
        tabla_propiedades.loc['6s','Título de vapor']=None
        tabla_propiedades.loc['6','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']
        tabla_propiedades.loc['7','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']
        tabla_propiedades.loc['8','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']
        tabla_propiedades.loc['11','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']-tabla_propiedades.loc['3','Caudal másico (Kg/s)']
        tabla_propiedades.loc['9','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
        tabla_propiedades.loc['10','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
        tabla_propiedades.loc['1','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
        tabla_propiedades.loc['2','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
        tabla_propiedades.loc['12','Caudal másico (Kg/s)']=0
        tabla_propiedades.loc['13','Caudal másico (Kg/s)']=0
        tabla_propiedades.loc['14','Caudal másico (Kg/s)']=tabla_propiedades.loc['11','Caudal másico (Kg/s)']

    else:
        def calcular(variables):
            m_3,m_5,m_13=variables

            tabla_propiedades.loc['3','Caudal másico (Kg/s)']=m_3
            tabla_propiedades.loc['5','Caudal másico (Kg/s)']=m_5
            tabla_propiedades.loc['3','Densidad (Kg/m^3)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']/((8*(R_volumetrico_baja_teorico/100)*F)/10**6)
            tabla_propiedades.loc['5','Densidad (Kg/m^3)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']/((5.6*(R_volumetrico_alta_teorico/100)*F)/10**6)

            tabla_propiedades.loc['3','Presión (bar)']=presion_evaporacion
            tabla_propiedades.loc['3','Temperatura (°C)']=(CP.PropsSI("T", "P",presion_evaporacion*(10**5) , "D", tabla_propiedades.loc['3','Densidad (Kg/m^3)'], "CO2"))-273.15
            tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",presion_evaporacion*(10**5) , "D", tabla_propiedades.loc['3','Densidad (Kg/m^3)'], "CO2"))/1000
            tabla_propiedades.loc['3','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",presion_evaporacion*(10**5) , "D",tabla_propiedades.loc['3','Densidad (Kg/m^3)'], "CO2"))/1000

            tabla_propiedades.loc['5','Presión (bar)']=media['Presion deposito (bar)']
            tabla_propiedades.loc['5','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))-273.15
            tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000
            tabla_propiedades.loc['5','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D",tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000

            tabla_propiedades.loc['4s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']
            tabla_propiedades.loc['4s','Presión (bar)']=media['Presion deposito (bar)']
            tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media['Presion deposito (bar)']*(10**5) , "S",tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
            tabla_propiedades.loc['4s','Temperatura (°C)']=(CP.PropsSI("T", "P",media['Presion deposito (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
            tabla_propiedades.loc['4s','Caudal másico (Kg/s)']=0
            tabla_propiedades.loc['4s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion deposito (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2")

            tabla_propiedades.loc['6s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']
            tabla_propiedades.loc['6s','Presión (bar)']=media['Presion condensacion (bar)']
            tabla_propiedades.loc['6s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media['Presion condensacion (bar)']*(10**5) , "S",tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
            tabla_propiedades.loc['6s','Temperatura (°C)']=(CP.PropsSI("T", "P",media['Presion condensacion (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
            tabla_propiedades.loc['6s','Caudal másico (Kg/s)']=0
            tabla_propiedades.loc['6s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion condensacion (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2")

            tabla_propiedades.loc['4','Entalpía (kJ/Kg)']=tabla_propiedades.loc['3','Entalpía (kJ/Kg)']+(tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])/(R_isentropico/100)
            tabla_propiedades.loc['4','Presión (bar)']=media['Presion deposito (bar)']
            tabla_propiedades.loc['4','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media['Presion deposito (bar)']*(10**5) , "H",tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
            tabla_propiedades.loc['4','Temperatura (°C)']=(CP.PropsSI("T", "P",media['Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))-273.15
            tabla_propiedades.loc['4','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media['Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2")
            tabla_propiedades.loc['4','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
            tabla_propiedades.loc['4','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media['Presion deposito (bar)']*(10**5) , "H",tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))/1000

            tabla_propiedades.loc['13','Caudal másico (Kg/s)']=m_13
            tabla_propiedades.loc['12','Caudal másico (Kg/s)']=m_13

            H_6=tabla_propiedades.loc['5','Entalpía (kJ/Kg)']+(tabla_propiedades.loc['6s','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])/(R_isentropico/100)
            M_5_balance=m_5*tabla_propiedades.loc['8','Título de vapor']-m_13+m_3          
            h_3=tabla_propiedades.loc['3','Entalpía (kJ/Kg)']
            H_3_balance=(m_5*(1-tabla_propiedades.loc['8','Título de vapor'])*tabla_propiedades.loc['2','Entalpía (kJ/Kg)']+m_13*tabla_propiedades.loc['13','Entalpía (kJ/Kg)'])/m_3


            error_punto_6=abs(H_6-tabla_propiedades.loc['6','Entalpía (kJ/Kg)'])
            error_m_5=abs(m_5-M_5_balance)
            error_punto_3=abs(h_3-H_3_balance)

        #Combinación de objetivos (método de suma ponderada)
            peso_punto_6 = 0.3  
            peso_m_5 = 0.4  
            peso_punto_3=0.3
            return error_punto_6*peso_punto_6+error_m_5*peso_m_5+error_punto_3*peso_punto_3

        resultado = minimize(calcular,
        x0=[0.01, 0.015,0.005],
        bounds=[(0.005, 0.025), (0.01, 0.03),(0.0005,0.005)],
        method='L-BFGS-B',
        options={'ftol': 1e-4}
        )
    
        tabla_propiedades.loc['4','Título de vapor']=None
        tabla_propiedades.loc['3','Título de vapor']=None
        tabla_propiedades.loc['4s','Título de vapor']=None
        tabla_propiedades.loc['5','Título de vapor']=None
        tabla_propiedades.loc['6s','Título de vapor']=None
        tabla_propiedades.loc['6','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']
        tabla_propiedades.loc['7','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']
        tabla_propiedades.loc['8','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']
        tabla_propiedades.loc['11','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']*tabla_propiedades.loc['8','Título de vapor']
        tabla_propiedades.loc['9','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(1-tabla_propiedades.loc['8','Título de vapor'])
        tabla_propiedades.loc['10','Caudal másico (Kg/s)']=tabla_propiedades.loc['9','Caudal másico (Kg/s)']
        tabla_propiedades.loc['1','Caudal másico (Kg/s)']=tabla_propiedades.loc['9','Caudal másico (Kg/s)']
        tabla_propiedades.loc['2','Caudal másico (Kg/s)']=tabla_propiedades.loc['9','Caudal másico (Kg/s)']
        tabla_propiedades.loc['14','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']-tabla_propiedades.loc['3','Caudal másico (Kg/s)']


    columnas=['Temperatura (°C)','Presión (bar)','Entalpía (kJ/Kg)','Entropía (kJ/Kg·K)','Densidad (Kg/m^3)']
    tabla_propiedades[columnas] = tabla_propiedades[columnas].apply(pd.to_numeric, errors='coerce')
    tabla_propiedades[columnas] = tabla_propiedades[columnas].round(3)
    tabla_propiedades.loc['6s','Caudal másico (Kg/s)']=None
    tabla_propiedades.loc['4s','Caudal másico (Kg/s)']=None
    tabla_propiedades['Caudal másico (Kg/s)'] = tabla_propiedades['Caudal másico (Kg/s)'].round(4)

    #REPRESENTACIÓN
    #Tabla de propiedades termodinámicas
    st.markdown("<br>", unsafe_allow_html=True) 
        
    st.markdown("<p style='font-size: 17px;'><strong>Propiedades termodinámicas</strong></p>", unsafe_allow_html=True)
    tabla_propiedades.index.name = "Puntos"
    st.dataframe(tabla_propiedades,height=400,use_container_width=True,hide_index=False)

    st.markdown("<br>", unsafe_allow_html=True) 
    

    #Diagramas ph y ts

    #Curvas de saturación
    presion = np.linspace(CP.PropsSI('CO2', 'ptriple'), CP.PropsSI('CO2', 'pcrit') , 1000)
    h_liq = [CP.PropsSI('H', 'P', pi, 'Q', 0, "CO2")/1000 for pi in presion]  
    h_vap = [CP.PropsSI('H', 'P', pi, 'Q', 1, "CO2")/1000 for pi in presion]  
    s_liq = [CP.PropsSI('S', 'P', pi, 'Q', 0, "CO2")/1000 for pi in presion]  
    s_vap = [CP.PropsSI('S', 'P', pi, 'Q', 1, "CO2")/1000 for pi in presion]  
    T_liq = [CP.PropsSI('T', 'P', pi, 'Q', 0, "CO2")-273.15 for pi in presion]  
    T_vap = [CP.PropsSI('T', 'P', pi, 'Q', 1, "CO2")-273.15 for pi in presion]  
    
    # Crear subplots en una fila
    fig = make_subplots(rows=1, cols=2, subplot_titles=("<b>P-H</b>", "<b>T-S</b>"))
    fig.update_annotations(font=dict(color='black', size=16))
  

    # Diagrama P-h
    puntos_ciclo_ph={'x':[tabla_propiedades.loc['1','Entalpía (kJ/Kg)'],tabla_propiedades.loc['2','Entalpía (kJ/Kg)'],tabla_propiedades.loc['3','Entalpía (kJ/Kg)'],tabla_propiedades.loc['4','Entalpía (kJ/Kg)'],tabla_propiedades.loc['5','Entalpía (kJ/Kg)'],tabla_propiedades.loc['6','Entalpía (kJ/Kg)'],tabla_propiedades.loc['7','Entalpía (kJ/Kg)'],tabla_propiedades.loc['8','Entalpía (kJ/Kg)'],tabla_propiedades.loc['9','Entalpía (kJ/Kg)'],tabla_propiedades.loc['10','Entalpía (kJ/Kg)'],tabla_propiedades.loc['1','Entalpía (kJ/Kg)']],
                     'y':[tabla_propiedades.loc['1','Presión (bar)'],tabla_propiedades.loc['2','Presión (bar)'],tabla_propiedades.loc['3','Presión (bar)'],tabla_propiedades.loc['4','Presión (bar)'],tabla_propiedades.loc['5','Presión (bar)'],tabla_propiedades.loc['6','Presión (bar)'],tabla_propiedades.loc['7','Presión (bar)'],tabla_propiedades.loc['8','Presión (bar)'],tabla_propiedades.loc['9','Presión (bar)'],tabla_propiedades.loc['10','Presión (bar)'],tabla_propiedades.loc['1','Presión (bar)']]}

    puntos_ciclo_ph_2={'x':[tabla_propiedades.loc['8','Entalpía (kJ/Kg)'],tabla_propiedades.loc['11','Entalpía (kJ/Kg)'],tabla_propiedades.loc['5','Entalpía (kJ/Kg)']],
                     'y':[tabla_propiedades.loc['8','Presión (bar)'],tabla_propiedades.loc['11','Presión (bar)'],tabla_propiedades.loc['5','Presión (bar)']]}
    puntos_ciclo_ph_3={'x':[tabla_propiedades.loc['11','Entalpía (kJ/Kg)'],tabla_propiedades.loc['13','Entalpía (kJ/Kg)']],
                     'y':[tabla_propiedades.loc['11','Presión (bar)'],tabla_propiedades.loc['13','Presión (bar)']]}

    puntos_ciclo_ph_4={'x':[tabla_propiedades.loc['3','Entalpía (kJ/Kg)'],tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']],
                     'y':[tabla_propiedades.loc['3','Presión (bar)'],tabla_propiedades.loc['4s','Presión (bar)']]}
    
    puntos_ciclo_ph_5={'x':[tabla_propiedades.loc['5','Entalpía (kJ/Kg)'],tabla_propiedades.loc['6s','Entalpía (kJ/Kg)']],
                     'y':[tabla_propiedades.loc['5','Presión (bar)'],tabla_propiedades.loc['6s','Presión (bar)']]}

    fig.add_trace(go.Scatter(x=h_liq, y=(presion/1e5),mode='lines', name='Líquido saturado', line=dict(color='blue'),hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
    fig.add_trace(go.Scatter(x=h_vap, y=(presion/1e5),mode='lines', name='Vapor saturado', line=dict(color='red'),hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1) 
    fig.add_trace(go.Scatter(x=puntos_ciclo_ph_3['x'],y=puntos_ciclo_ph_3['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ph_2['x'],y=puntos_ciclo_ph_2['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ph['x'],y=puntos_ciclo_ph['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ph_4['x'],y=puntos_ciclo_ph_4['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ph_5['x'],y=puntos_ciclo_ph_5['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
    #presion_ticks=[0,10,20,30,40,50,60,70,80]
    #fig.update_yaxes(title_text="Presión (bar)", type="log",tickvals=presion_ticks,ticktext=[f"{p:.0f}" for p in presion_ticks],range=[np.log10(CP.PropsSI('CO2', 'ptriple')/1e5), np.log10(CP.PropsSI('CO2', 'pcrit')/1e5)], row=1, col=1)
    fig.update_yaxes(title_text="Presión (bar)", row=1, col=1,showgrid=False,mirror=False,zeroline=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))
    fig.update_xaxes(title_text="Entalpía (kJ/Kg)", row=1, col=1,showgrid=False,mirror=False,zeroline=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))

    # Diagrama T-s
    puntos_ciclo_ts={'x':[tabla_propiedades.loc['3','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['4','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['3','Temperatura (°C)'],tabla_propiedades.loc['4','Temperatura (°C)']]}
    
    puntos_ciclo_ts_6={'x':[tabla_propiedades.loc['5','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['6','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['5','Temperatura (°C)'],tabla_propiedades.loc['6','Temperatura (°C)']]}

    puntos_ciclo_ts_2={'x':[tabla_propiedades.loc['8','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['11','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['8','Temperatura (°C)'],tabla_propiedades.loc['11','Temperatura (°C)']]}
    puntos_ciclo_ts_3={'x':[tabla_propiedades.loc['11','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['13','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['11','Temperatura (°C)'],tabla_propiedades.loc['13','Temperatura (°C)']]}

    puntos_ciclo_ts_4={'x':[tabla_propiedades.loc['3','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['4s','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['3','Temperatura (°C)'],tabla_propiedades.loc['4s','Temperatura (°C)']]}
    
    puntos_ciclo_ts_5={'x':[tabla_propiedades.loc['5','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['6s','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['5','Temperatura (°C)'],tabla_propiedades.loc['6s','Temperatura (°C)']]}
    
    puntos_ciclo_ts_7={'x':[tabla_propiedades.loc['7','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['8','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['9','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['10','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['13','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['1','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['7','Temperatura (°C)'],tabla_propiedades.loc['8','Temperatura (°C)'],tabla_propiedades.loc['9','Temperatura (°C)'],tabla_propiedades.loc['10','Temperatura (°C)'],tabla_propiedades.loc['13','Temperatura (°C)'],tabla_propiedades.loc['1','Temperatura (°C)']]}
    
    puntos_ciclo_ts_8={'x':[tabla_propiedades.loc['1','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['2','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['1','Temperatura (°C)'],tabla_propiedades.loc['2','Temperatura (°C)'],tabla_propiedades.loc['3','Temperatura (°C)']]}


    entropia_isobara_alta =(np.linspace(tabla_propiedades.loc['7','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['6','Entropía (kJ/Kg·K)'] , 20))*1000
    temperatura_isobara_alta = [CP.PropsSI('T', 'S', s, 'P', tabla_propiedades.loc['6','Presión (bar)']*(10**5), "CO2")-273.15 for s in entropia_isobara_alta] 

    entropia_isobara_intermedia=(np.linspace(tabla_propiedades.loc['11','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['4','Entropía (kJ/Kg·K)'] , 20))*1000
    temperatura_isobara_intermedia=[CP.PropsSI('T', 'S', s, 'P', tabla_propiedades.loc['11','Presión (bar)']*(10**5), "CO2")-273.15 for s in entropia_isobara_intermedia] 


    fig.add_trace(go.Scatter(x=s_liq, y=T_liq,mode='lines', name='Líquido saturado', line=dict(color='blue'), showlegend=False,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=s_vap, y=T_liq,mode='lines', name='Vapor saturado', line=dict(color='red'), showlegend=False,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ts_3['x'],y=puntos_ciclo_ts_3['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ts_6['x'],y=puntos_ciclo_ts_6['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ts_2['x'],y=puntos_ciclo_ts_2['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ts['x'],y=puntos_ciclo_ts['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ts_4['x'],y=puntos_ciclo_ts_4['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ts_5['x'],y=puntos_ciclo_ts_5['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ts_7['x'],y=puntos_ciclo_ts_7['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=puntos_ciclo_ts_8['x'],y=puntos_ciclo_ts_8['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
      
    fig.add_trace(go.Scatter(x=entropia_isobara_alta/1000,y=temperatura_isobara_alta,mode='lines',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
    fig.add_trace(go.Scatter(x=entropia_isobara_intermedia/1000,y=temperatura_isobara_intermedia,mode='lines',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)



    fig.update_yaxes(title_text="Temperatura (°C)", row=1, col=2,showgrid=False,zeroline=False,mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))
    fig.update_xaxes(title_text="Entropía (kJ/Kg·K)", row=1, col=2,showgrid=False,zeroline=False,mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))

    # Ajustes finales
    fig.update_layout(height=600,width=1200,title_text="Diagramas ciclo",title_font=dict(size=16,family='Arial'),hovermode="closest",showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    #Análisis energético
    st.markdown("<br>", unsafe_allow_html=True) 
        
    st.markdown("<p style='font-size: 17px;'><strong>Análisis energético</strong></p>", unsafe_allow_html=True)
  


    tabla_propiedades_balance=pd.DataFrame(columns=['Valores','Unidades'],index=['Potencia frigorífica (evaporadores)','Potencia cedida (gas-cooler)','Potencia ideal (compresor)','Consumo eléctrico (compresor)','COP (EER)','COP (BC)'])
    tabla_propiedades_balance.index.name = "Variables"
    tabla_propiedades_balance.loc['Potencia frigorífica (evaporadores)','Unidades']='kW'
    tabla_propiedades_balance.loc['Potencia ideal (compresor)','Unidades']='kW'
    tabla_propiedades_balance.loc['Potencia cedida (gas-cooler)','Unidades']='kW'
    tabla_propiedades_balance.loc['COP (EER)','Unidades']='-'
    tabla_propiedades_balance.loc['COP (BC)','Unidades']='-'  
    tabla_propiedades_balance.loc['Consumo eléctrico (compresor)','Unidades']='kW'

    tabla_propiedades_balance.loc['Consumo eléctrico (compresor)','Valores']=media['Potencia total (W)']/1000
    tabla_propiedades_balance.loc['Potencia frigorífica (evaporadores)','Valores']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['1','Entalpía (kJ/Kg)']-tabla_propiedades.loc['10','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['2','Entalpía (kJ/Kg)']-tabla_propiedades.loc['1','Entalpía (kJ/Kg)'])
    tabla_propiedades_balance.loc['Potencia ideal (compresor)','Valores']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']*(tabla_propiedades.loc['4','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])
    tabla_propiedades_balance.loc['Potencia cedida (gas-cooler)','Valores']=tabla_propiedades.loc['6','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['7','Entalpía (kJ/Kg)'])
    tabla_propiedades_balance.loc['COP (EER)','Valores']=tabla_propiedades_balance.loc['Potencia frigorífica (evaporadores)','Valores']/(media['Potencia total (W)']/1000)
    tabla_propiedades_balance.loc['COP (BC)','Valores']=tabla_propiedades_balance.loc['Potencia cedida (gas-cooler)','Valores']/(media['Potencia total (W)']/1000)


    st.dataframe(tabla_propiedades_balance,height=245,use_container_width=True,hide_index=False)

    #Análisis compresor
    st.markdown("<br>", unsafe_allow_html=True) 
        
    st.markdown("<p style='font-size: 17px;'><strong>Análisis compresor</strong></p>", unsafe_allow_html=True)
  


    tabla_propiedades_compresor=pd.DataFrame(columns=['Valores','Unidades'],index=['Velocidad de giro','Capacidad de desplazamiento (primera etapa)','Capacidad de desplazamiento (segunda etapa)','Flujo másico geométrico (primera etapa)','Flujo másico geométrico (segunda etapa)','Flujo másico (primera etapa)','Flujo másico (segunda etapa)','Rendimiento isentrópico (primera etapa)','Rendimiento isentrópico (segunda etapa)','Rendimiento volumétrico (primera etapa)','Rendimiento volumétrico (segunda etapa)','Rendimiento electromecánico','Consumo de energía isentrópica ideal','Consumo eléctrico'])
    tabla_propiedades_compresor.index.name = "Variables"
    tabla_propiedades_compresor.loc['Velocidad de giro','Unidades']='rev/s'
    tabla_propiedades_compresor.loc['Capacidad de desplazamiento (primera etapa)','Unidades']='cm^3/rev'
    tabla_propiedades_compresor.loc['Capacidad de desplazamiento (segunda etapa)','Unidades']='cm^3/rev' 
    tabla_propiedades_compresor.loc['Flujo másico geométrico (primera etapa)','Unidades']='Kg/s' 
    tabla_propiedades_compresor.loc['Flujo másico geométrico (segunda etapa)','Unidades']='Kg/s' 
    tabla_propiedades_compresor.loc['Flujo másico (primera etapa)','Unidades']='Kg/s' 
    tabla_propiedades_compresor.loc['Flujo másico (segunda etapa)','Unidades']='Kg/s' 
    tabla_propiedades_compresor.loc['Rendimiento isentrópico (primera etapa)','Unidades']='%' 
    tabla_propiedades_compresor.loc['Rendimiento isentrópico (segunda etapa)','Unidades']='%' 
    tabla_propiedades_compresor.loc['Rendimiento volumétrico (primera etapa)','Unidades']='%' 
    tabla_propiedades_compresor.loc['Rendimiento volumétrico (segunda etapa)','Unidades']='%' 
    tabla_propiedades_compresor.loc['Rendimiento electromecánico','Unidades']='%' 
    tabla_propiedades_compresor.loc['Consumo de energía isentrópica ideal','Unidades']='kW' 
    tabla_propiedades_compresor.loc['Consumo eléctrico','Unidades']='kW' 

    tabla_propiedades_compresor.loc['Velocidad de giro','Valores']=F
    tabla_propiedades_compresor.loc['Capacidad de desplazamiento (primera etapa)','Valores']=8
    tabla_propiedades_compresor.loc['Capacidad de desplazamiento (segunda etapa)','Valores']=5.6
    tabla_propiedades_compresor.loc['Flujo másico geométrico (primera etapa)','Valores']=F*8*tabla_propiedades.loc['3','Densidad (Kg/m^3)']/10**6
    tabla_propiedades_compresor.loc['Flujo másico geométrico (segunda etapa)','Valores']=F*5.6*tabla_propiedades.loc['5','Densidad (Kg/m^3)']/10**6
    tabla_propiedades_compresor.loc['Flujo másico (primera etapa)','Valores']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
    tabla_propiedades_compresor.loc['Flujo másico (segunda etapa)','Valores']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']
    tabla_propiedades_compresor.loc['Rendimiento isentrópico (primera etapa)','Valores']=round(R_isentropico,2)
    tabla_propiedades_compresor.loc['Rendimiento isentrópico (segunda etapa)','Valores']= round(R_isentropico,2)
    tabla_propiedades_compresor.loc['Rendimiento volumétrico (primera etapa)','Valores']=round(R_volumetrico_baja_teorico,2)
    tabla_propiedades_compresor.loc['Rendimiento volumétrico (segunda etapa)','Valores']=round(R_volumetrico_alta_teorico,2)
    tabla_propiedades_compresor.loc['Consumo de energía isentrópica ideal','Valores']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']*(tabla_propiedades.loc['4','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])
    tabla_propiedades_compresor.loc['Consumo eléctrico','Valores']=round(media['Potencia total (W)']/1000,3)
    tabla_propiedades_compresor.loc['Rendimiento electromecánico','Valores']=round(tabla_propiedades_compresor.loc['Consumo de energía isentrópica ideal','Valores']*100/tabla_propiedades_compresor.loc['Consumo eléctrico','Valores'],2)

    st.dataframe(tabla_propiedades_compresor,height=400,use_container_width=True,hide_index=False)

    #Análisis evaporadores
    st.markdown("<br>", unsafe_allow_html=True) 
        
    st.markdown("<p style='font-size: 17px;'><strong>Análisis evaporadores</strong></p>", unsafe_allow_html=True)
  
    tabla_propiedades_evaporadores=pd.DataFrame(columns=['Valores','Unidades'],index=['Potencia (ventiladores)','Velocidad de giro (ventiladores)','Caudal (aire - total)','Temperatura entrada (aire - evaporador 1)','Temperatura salida (aire - evaporador 1)','Temperatura entrada (aire - evaporador 2)','Temperatura salida (aire - evaporador 2)','Transferencia térmica (aire - evaporador 1)','Transferencia térmica (aire - evaporador 2)','Transferencia térmica (aire - total)','Flujo másico (refrigerante - total)','Transferencia térmica (refrigerante - total)','Efectividad (evaporador 1)','Efectividad (evaporador 2)','Discrepancia térmica (evaporador 1)','Discrepancia térmica (evaporador 2)','Salto térmico (entrada - evaporador 1)','Salto térmico (salida - evaporador 1)','Salto térmico (entrada - evaporador 2)','Salto térmico (salida - evaporador 2)','Sobrecalentamiento (evaporador 1)','Sobrecalentamiento (evaporador 2)'])
    tabla_propiedades_evaporadores.index.name = "Variables"
    tabla_propiedades_evaporadores.loc['Potencia (ventiladores)','Unidades']='%'
    tabla_propiedades_evaporadores.loc['Velocidad de giro (ventiladores)','Unidades']='rpm'
    tabla_propiedades_evaporadores.loc['Caudal (aire - total)','Unidades']='m^3/s'
    tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 1)','Unidades']='°C'
    tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 1)','Unidades']='°C'
    tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 2)','Unidades']='°C'
    tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 2)','Unidades']='°C'
    tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 1)','Unidades']='kW'
    tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 2)','Unidades']='kW'
    tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - total)','Unidades']='kW'
    tabla_propiedades_evaporadores.loc['Flujo másico (refrigerante - total)','Unidades']='Kg/s'
    tabla_propiedades_evaporadores.loc['Transferencia térmica (refrigerante - total)','Unidades']='kW'
    tabla_propiedades_evaporadores.loc['Efectividad (evaporador 1)','Unidades']='%'
    tabla_propiedades_evaporadores.loc['Efectividad (evaporador 2)','Unidades']='%'
    tabla_propiedades_evaporadores.loc['Discrepancia térmica (evaporador 1)','Unidades']='%'
    tabla_propiedades_evaporadores.loc['Discrepancia térmica (evaporador 2)','Unidades']='%'
    tabla_propiedades_evaporadores.loc['Salto térmico (entrada - evaporador 1)','Unidades']='K'
    tabla_propiedades_evaporadores.loc['Salto térmico (salida - evaporador 1)','Unidades']='K'
    tabla_propiedades_evaporadores.loc['Salto térmico (entrada - evaporador 2)','Unidades']='K'
    tabla_propiedades_evaporadores.loc['Salto térmico (salida - evaporador 2)','Unidades']='K'
    tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 1)','Unidades']='K'
    tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 2)','Unidades']='K'

    tabla_propiedades_evaporadores.loc['Potencia (ventiladores)','Valores']=100
    tabla_propiedades_evaporadores.loc['Velocidad de giro (ventiladores)','Valores']=2600
    tabla_propiedades_evaporadores.loc['Caudal (aire - total)','Valores']=0.292
    tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 1)','Valores']=media['Temperatura camara (evaporador 1) (°C)']
    tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 1)','Valores']=media['Temperatura desescarche (evaporador 1) (°C)']
    tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 2)','Valores']=media['Temperatura camara (evaporador 2) (°C)']
    tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 2)','Valores']=media['Temperatura desescarche (evaporador 2) (°C)']
    tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 1)','Valores']=(0.292/2)*1.344*1.006*(media['Temperatura camara (evaporador 1) (°C)']-media['Temperatura desescarche (evaporador 1) (°C)'])
    tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 2)','Valores']=(0.292/2)*1.344*1.006*(media['Temperatura camara (evaporador 2) (°C)']-media['Temperatura desescarche (evaporador 2) (°C)'])
    tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - total)','Valores']=tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 1)','Valores']+tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 2)','Valores']
    tabla_propiedades_evaporadores.loc['Flujo másico (refrigerante - total)','Valores']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']
    tabla_propiedades_evaporadores.loc['Transferencia térmica (refrigerante - total)','Valores']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['1','Entalpía (kJ/Kg)']-tabla_propiedades.loc['10','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['2','Entalpía (kJ/Kg)']-tabla_propiedades.loc['1','Entalpía (kJ/Kg)'])
    tabla_propiedades_evaporadores.loc['Efectividad (evaporador 1)','Valores']=round((media['Temperatura camara (evaporador 1) (°C)']-media['Temperatura desescarche (evaporador 1) (°C)'])*100/(media['Temperatura camara (evaporador 1) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),2)
    tabla_propiedades_evaporadores.loc['Efectividad (evaporador 2)','Valores']=round((media['Temperatura camara (evaporador 2) (°C)']-media['Temperatura desescarche (evaporador 2) (°C)'])*100/(media['Temperatura camara (evaporador 2) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),2)
    tabla_propiedades_evaporadores.loc['Discrepancia térmica (evaporador 1)','Valores']=round(tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 1)','Valores']*100/(tabla_propiedades_evaporadores.loc['Transferencia térmica (refrigerante - total)','Valores']/2),2)
    tabla_propiedades_evaporadores.loc['Discrepancia térmica (evaporador 2)','Valores']=round(tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 2)','Valores']*100/(tabla_propiedades_evaporadores.loc['Transferencia térmica (refrigerante - total)','Valores']/2),2)
    tabla_propiedades_evaporadores.loc['Salto térmico (entrada - evaporador 1)','Valores']=tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 1)','Valores']-tabla_propiedades.loc['2','Temperatura (°C)']
    tabla_propiedades_evaporadores.loc['Salto térmico (salida - evaporador 1)','Valores']=tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 1)','Valores']-tabla_propiedades.loc['1','Temperatura (°C)']
    tabla_propiedades_evaporadores.loc['Salto térmico (entrada - evaporador 2)','Valores']=tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 2)','Valores']-tabla_propiedades.loc['2','Temperatura (°C)']
    tabla_propiedades_evaporadores.loc['Salto térmico (salida - evaporador 2)','Valores']=tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 2)','Valores']-tabla_propiedades.loc['1','Temperatura (°C)']
    if ('Recalentamiento (valvula expansion 1) (K)' in media.index) and ('Recalentamiento (valvula expansion 2) (K)' in media.index):
        tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 1)','Valores']=round(media['Recalentamiento (valvula expansion 1) (K)'],3)
        tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 2)','Valores']=round(media['Recalentamiento (valvula expansion 2) (K)'],3)
    else:
        tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 1)','Valores']=round(abs(tabla_propiedades.loc['2','Temperatura (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),3)
        tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 2)','Valores']=round(abs(tabla_propiedades.loc['2','Temperatura (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),3)
    
    st.dataframe(tabla_propiedades_evaporadores,height=400,use_container_width=True,hide_index=False)


    
    # Crear subplots en una fila
    fig2 = make_subplots(rows=1, cols=2, subplot_titles=("<b>Evaporador 1</b>", "<b>Evaporador 2</b>"))
    fig2.update_annotations(font=dict(color='black', size=16))

    puntos_ciclo_refrigerante={'x':[tabla_propiedades.loc['10','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['1','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['2','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['10','Temperatura (°C)'],tabla_propiedades.loc['1','Temperatura (°C)'],tabla_propiedades.loc['2','Temperatura (°C)']]}

    puntos_ciclo_aire={'x':[tabla_propiedades.loc['10','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['2','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 1)','Valores'],tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 1)','Valores']]}

    puntos_salto_entrada={'x':[tabla_propiedades.loc['2','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['2','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['2','Temperatura (°C)'],tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 1)','Valores']]}
    diferencia_temperatura_entrada = abs(puntos_salto_entrada['y'][0] - puntos_salto_entrada['y'][1])


    puntos_salto_salida={'x':[tabla_propiedades.loc['10','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['10','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['10','Temperatura (°C)'],tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 1)','Valores']]}
    diferencia_temperatura_salida = abs(puntos_salto_salida['y'][0] - puntos_salto_salida['y'][1])


    fig2.add_trace(go.Scatter(x=puntos_ciclo_refrigerante['x'],y=puntos_ciclo_refrigerante['y'],mode='lines+markers',name='Refrigerante',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C"), row=1, col=1)
    fig2.add_trace(go.Scatter(x=puntos_ciclo_aire['x'],y=puntos_ciclo_aire['y'],mode='lines+markers',name='Aire',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C"), row=1, col=1)

    fig2.add_trace(go.Scatter(x=puntos_salto_entrada['x'],y=puntos_salto_entrada['y'],mode='lines',name='Salto térmico entrada',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C"), row=1, col=1)
    fig2.add_trace(go.Scatter(x=puntos_salto_salida['x'],y=puntos_salto_salida['y'],mode='lines',name='Salto térmico salida',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C"), row=1, col=1)

    pos_x_entrada = (puntos_salto_entrada['x'][0] + puntos_salto_entrada['x'][1]) / 2
    pos_y_entrada = (puntos_salto_entrada['y'][0] + puntos_salto_entrada['y'][1]) / 2

    fig2.add_annotation(x=pos_x_entrada, y=pos_y_entrada, text=f"Salto térmico entrada: {diferencia_temperatura_entrada:.2f} K",font=dict(size=12, color="black"),bgcolor="white",showarrow=False, row=1, col=1)
    pos_x_salida = (puntos_salto_salida['x'][0] + puntos_salto_salida['x'][1]) / 2
    pos_y_salida = (puntos_salto_salida['y'][0] + puntos_salto_salida['y'][1]) / 2

    fig2.add_annotation(x=pos_x_salida, y=pos_y_salida, text=f"Salto térmico salida: {diferencia_temperatura_salida:.2f} K",font=dict(size=12, color="black"),bgcolor="white",showarrow=False, row=1, col=1)

    fig2.update_yaxes(title_text="Temperatura (°C)", row=1, col=1,showgrid=False,zeroline=False,mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))
    fig2.update_xaxes(title_text="", row=1, col=1,showgrid=False,zeroline=False,mirror=False,linecolor='black',tickfont=dict(color='black'),showticklabels=False,title=dict(font=dict(color='black')))




    puntos_ciclo_aire_2={'x':[tabla_propiedades.loc['10','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['2','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 2)','Valores'],tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 2)','Valores']]}

    puntos_salto_entrada_2={'x':[tabla_propiedades.loc['2','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['2','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['2','Temperatura (°C)'],tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 2)','Valores']]}
    diferencia_temperatura_entrada_2 = abs(puntos_salto_entrada_2['y'][0] - puntos_salto_entrada_2['y'][1])


    puntos_salto_salida_2={'x':[tabla_propiedades.loc['10','Entropía (kJ/Kg·K)'],tabla_propiedades.loc['10','Entropía (kJ/Kg·K)']],
                     'y':[tabla_propiedades.loc['10','Temperatura (°C)'],tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 2)','Valores']]}
    diferencia_temperatura_salida_2 = abs(puntos_salto_salida_2['y'][0] - puntos_salto_salida_2['y'][1])


    fig2.add_trace(go.Scatter(x=puntos_ciclo_refrigerante['x'],y=puntos_ciclo_refrigerante['y'],mode='lines+markers',name='Refrigerante',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C"), row=1, col=2)
    fig2.add_trace(go.Scatter(x=puntos_ciclo_aire_2['x'],y=puntos_ciclo_aire_2['y'],mode='lines+markers',name='Aire',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C"), row=1, col=2)

    fig2.add_trace(go.Scatter(x=puntos_salto_entrada_2['x'],y=puntos_salto_entrada_2['y'],mode='lines',name='Salto térmico entrada',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C"), row=1, col=2)
    fig2.add_trace(go.Scatter(x=puntos_salto_salida_2['x'],y=puntos_salto_salida_2['y'],mode='lines',name='Salto térmico salida',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C"), row=1, col=2)

    pos_x_entrada_2 = (puntos_salto_entrada_2['x'][0] + puntos_salto_entrada_2['x'][1]) / 2
    pos_y_entrada_2 = (puntos_salto_entrada_2['y'][0] + puntos_salto_entrada_2['y'][1]) / 2

    fig2.add_annotation(x=pos_x_entrada_2, y=pos_y_entrada_2, text=f"Salto térmico entrada: {diferencia_temperatura_entrada_2:.2f} K",font=dict(size=12, color="black"),bgcolor="white",showarrow=False, row=1, col=2)
    pos_x_salida_2 = (puntos_salto_salida_2['x'][0] + puntos_salto_salida_2['x'][1]) / 2
    pos_y_salida_2 = (puntos_salto_salida_2['y'][0] + puntos_salto_salida_2['y'][1]) / 2

    fig2.add_annotation(x=pos_x_salida_2, y=pos_y_salida_2, text=f"Salto térmico salida: {diferencia_temperatura_salida_2:.2f} K",font=dict(size=12, color="black"),bgcolor="white",showarrow=False, row=1, col=2)

    fig2.update_yaxes(title_text="Temperatura (°C)", row=1, col=2,showgrid=False,zeroline=False,mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))
    fig2.update_xaxes(title_text="", row=1, col=2,showgrid=False,zeroline=False,mirror=False,linecolor='black',tickfont=dict(color='black'),showticklabels=False,title=dict(font=dict(color='black')))

    # Ajustes finales
    fig2.update_layout(height=600,width=1200,title_text="Diagramas evaporadores",title_font=dict(size=16,family='Arial'),hovermode="closest",showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)


    #Análisis gas-cooler
    #st.markdown("<br>", unsafe_allow_html=True) 
        
    st.markdown("<p style='font-size: 17px;'><strong>Análisis gas-cooler</strong></p>", unsafe_allow_html=True)
  
    tabla_propiedades_gascooler=pd.DataFrame(columns=['Valores','Unidades'],index=['Potencia (ventilador)','Velocidad de giro (ventilador)','Caudal (aire)','Temperatura exterior','Flujo másico (refrigerante)','Transferencia térmica (refrigerante)','Salto térmico (salida)'])
    tabla_propiedades_gascooler.index.name = "Variables"


    tabla_propiedades_gascooler.loc['Potencia (ventilador)','Unidades']='%'
    tabla_propiedades_gascooler.loc['Velocidad de giro (ventilador)','Unidades']='rpm'
    tabla_propiedades_gascooler.loc['Temperatura exterior','Unidades']='°C'
    tabla_propiedades_gascooler.loc['Caudal (aire)','Unidades']='m^3/s'
    tabla_propiedades_gascooler.loc['Flujo másico (refrigerante)','Unidades']='Kg/s'
    tabla_propiedades_gascooler.loc['Transferencia térmica (refrigerante)','Unidades']='kW'
    tabla_propiedades_gascooler.loc['Salto térmico (salida)','Unidades']='K'

    tabla_propiedades_gascooler.loc['Potencia (ventilador)','Valores']=media['Potencia ventilador gas-cooler (%)']
    tabla_propiedades_gascooler.loc['Velocidad de giro (ventilador)','Valores']=970*media['Potencia ventilador gas-cooler (%)']/100
    tabla_propiedades_gascooler.loc['Temperatura exterior','Valores']=round(media['Temperatura exterior (°C)'],2)
    tabla_propiedades_gascooler.loc['Caudal (aire)','Valores']=3110*media['Potencia ventilador gas-cooler (%)']/(3600*100)
    tabla_propiedades_gascooler.loc['Flujo másico (refrigerante)','Valores']=tabla_propiedades.loc['6','Caudal másico (Kg/s)']
    tabla_propiedades_gascooler.loc['Transferencia térmica (refrigerante)','Valores']=tabla_propiedades.loc['6','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['7','Entalpía (kJ/Kg)'])
    tabla_propiedades_gascooler.loc['Salto térmico (salida)','Valores']=tabla_propiedades.loc['7','Temperatura (°C)']-media['Temperatura exterior (°C)']

    st.dataframe(tabla_propiedades_gascooler,height=280,use_container_width=True,hide_index=False)


    #Análisis gas-cooler
    st.markdown("<br>", unsafe_allow_html=True) 
        
    st.markdown("<p style='font-size: 17px;'><strong>Análisis válvulas electrónicas</strong></p>", unsafe_allow_html=True)
  
    tabla_propiedades_valvulas=pd.DataFrame(columns=['Valores','Unidades'],index=['Apertura (válvula alta presión)','Diferencial de presión (válvula alta presión)','Apertura (válvula by-pass)','Diferencial de presión (válvula by-pass)','Apertura (válvula expansión - evaporador 1)','Diferencial de presión (válvula expansión - evaporador 1)','Apertura (válvula expansión - evaporador 2)','Diferencial de presión (válvula expansión - evaporador 2)'])
    tabla_propiedades_valvulas.index.name = "Variables"

    tabla_propiedades_valvulas.loc['Apertura (válvula alta presión)','Unidades']='%'
    tabla_propiedades_valvulas.loc['Diferencial de presión (válvula alta presión)','Unidades']='bar'
    tabla_propiedades_valvulas.loc['Apertura (válvula by-pass)','Unidades']='%'
    tabla_propiedades_valvulas.loc['Diferencial de presión (válvula by-pass)','Unidades']='bar'
    tabla_propiedades_valvulas.loc['Apertura (válvula expansión - evaporador 1)','Unidades']='%'
    tabla_propiedades_valvulas.loc['Diferencial de presión (válvula expansión - evaporador 1)','Unidades']='bar'
    tabla_propiedades_valvulas.loc['Apertura (válvula expansión - evaporador 2)','Unidades']='%'
    tabla_propiedades_valvulas.loc['Diferencial de presión (válvula expansión - evaporador 2)','Unidades']='bar'


    tabla_propiedades_valvulas.loc['Apertura (válvula alta presión)','Valores']=media['Apertura valvula alta presion (%)']
    tabla_propiedades_valvulas.loc['Diferencial de presión (válvula alta presión)','Valores']=tabla_propiedades.loc['7','Presión (bar)']-tabla_propiedades.loc['8','Presión (bar)']
    tabla_propiedades_valvulas.loc['Apertura (válvula by-pass)','Valores']=media['Apertura valvula by-pass (%)']
    if media['Apertura valvula by-pass (%)']==0:
        tabla_propiedades_valvulas.loc['Diferencial de presión (válvula by-pass)','Valores']=0
    else:
        tabla_propiedades_valvulas.loc['Diferencial de presión (válvula by-pass)','Valores']=tabla_propiedades_gascooler.loc['Diferencial de presión (válvula expansión)','Valores']
    tabla_propiedades_valvulas.loc['Apertura (válvula expansión - evaporador 1)','Valores']=media['Apertura valvula (valvula expansion 1) (%)']
    tabla_propiedades_valvulas.loc['Diferencial de presión (válvula expansión - evaporador 1)','Valores']=tabla_propiedades.loc['9','Presión (bar)']-tabla_propiedades.loc['10','Presión (bar)']
    tabla_propiedades_valvulas.loc['Apertura (válvula expansión - evaporador 2)','Valores']=media['Apertura valvula (valvula expansion 2) (%)']
    tabla_propiedades_valvulas.loc['Diferencial de presión (válvula expansión - evaporador 2)','Valores']=tabla_propiedades.loc['9','Presión (bar)']-tabla_propiedades.loc['10','Presión (bar)']

    st.dataframe(tabla_propiedades_valvulas,height=315,use_container_width=True,hide_index=False)

    #Análisis flash-tank
    st.markdown("<br>", unsafe_allow_html=True) 
        
    st.markdown("<p style='font-size: 17px;'><strong>Análisis flash-tank</strong></p>", unsafe_allow_html=True)
  
    tabla_propiedades_deposito=pd.DataFrame(columns=['Valores','Unidades'],index=['Flujo másico (refrigerante bifásico)','Flujo másico (refrigerante vapor saturado)','Flujo másico (refrigerante líquido saturado)'])
    tabla_propiedades_deposito.index.name = "Variables"

    tabla_propiedades_deposito.loc['Flujo másico (refrigerante bifásico)','Unidades']='Kg/s'
    tabla_propiedades_deposito.loc['Flujo másico (refrigerante vapor saturado)','Unidades']='Kg/s'
    tabla_propiedades_deposito.loc['Flujo másico (refrigerante líquido saturado)','Unidades']='Kg/s'

    tabla_propiedades_deposito.loc['Flujo másico (refrigerante bifásico)','Valores']=tabla_propiedades.loc['7','Caudal másico (Kg/s)']
    tabla_propiedades_deposito.loc['Flujo másico (refrigerante vapor saturado)','Valores']=tabla_propiedades.loc['11','Caudal másico (Kg/s)']
    tabla_propiedades_deposito.loc['Flujo másico (refrigerante líquido saturado)','Valores']=tabla_propiedades.loc['9','Caudal másico (Kg/s)']
    st.dataframe(tabla_propiedades_deposito,height=140,use_container_width=True,hide_index=False)



  



