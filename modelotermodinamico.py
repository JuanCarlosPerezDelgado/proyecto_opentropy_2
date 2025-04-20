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


def calculo_modelo(temperatura_evaporacion,salto_evaporador,temperatura_ambiente,salto_gascooler,velocidad_compresor):

    F=velocidad_compresor

    tabla_propiedades=pd.DataFrame(columns=['Temperatura (°C)','Presión (bar)','Entalpía (kJ/Kg)','Entropía (kJ/Kg·K)','Título de vapor','Densidad (Kg/m^3)','Caudal másico (Kg/s)'],index=['1','2','3','4s','4','5','6s','6','7','8','9','10','11','12','13','14'])
    
    tabla_propiedades.loc['1','Temperatura (°C)']=temperatura_evaporacion #Temperatura de evaporación
    tabla_propiedades.loc['1','Título de vapor']=1.000
    tabla_propiedades.loc['1','Presión (bar)']=CP.PropsSI("P", "T", temperatura_evaporacion+273.15, "Q",1 , "CO2")/(10**5)
    tabla_propiedades.loc['1','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "T", temperatura_evaporacion+273.15, "Q",1 , "CO2"))/1000
    tabla_propiedades.loc['1','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "T", temperatura_evaporacion+273.15 , "Q", 1, "CO2"))/1000
    tabla_propiedades.loc['1','Densidad (Kg/m^3)']=CP.PropsSI("D", "T", temperatura_evaporacion+273.15 , "Q", 1, "CO2")

    tabla_propiedades.loc['2','Temperatura (°C)']=temperatura_evaporacion+salto_evaporador
    tabla_propiedades.loc['2','Presión (bar)']=tabla_propiedades.loc['1','Presión (bar)']
    tabla_propiedades.loc['2','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "T", tabla_propiedades.loc['2','Temperatura (°C)']+273.15, "P",tabla_propiedades.loc['1','Presión (bar)']*(10**5) , "CO2"))/1000
    tabla_propiedades.loc['2','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "T", tabla_propiedades.loc['2','Temperatura (°C)']+273.15 , "P", tabla_propiedades.loc['1','Presión (bar)']*(10**5), "CO2"))/1000
    tabla_propiedades.loc['2','Densidad (Kg/m^3)']=CP.PropsSI("D", "T", tabla_propiedades.loc['2','Temperatura (°C)']+273.15 , "P", tabla_propiedades.loc['1','Presión (bar)']*(10**5), "CO2")

    tabla_propiedades.loc['3','Presión (bar)']=tabla_propiedades.loc['2','Presión (bar)']
    tabla_propiedades.loc['10','Presión (bar)']=tabla_propiedades.loc['2','Presión (bar)']
    tabla_propiedades.loc['13','Presión (bar)']=tabla_propiedades.loc['2','Presión (bar)']


    tabla_propiedades.loc['7','Temperatura (°C)']=temperatura_ambiente+salto_gascooler
    presion_gascooler=39.222+(temperatura_ambiente)*(-0.0037939+(temperatura_ambiente)*(0.14681+(temperatura_ambiente)*(-0.0089186+(temperatura_ambiente)*(0.00034284+(temperatura_ambiente)*(-0.0000080028+(temperatura_ambiente)*0.000000087544)))))
    if presion_gascooler<80:
        presion_gascooler=80+1
    else:
        presion_gascooler=presion_gascooler+1
    tabla_propiedades.loc['7','Presión (bar)']=presion_gascooler
    tabla_propiedades.loc['7','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "T", tabla_propiedades.loc['7','Temperatura (°C)']+273.15, "P",presion_gascooler*(10**5) , "CO2"))/1000
    tabla_propiedades.loc['7','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "T", tabla_propiedades.loc['7','Temperatura (°C)']+273.15 , "P", presion_gascooler*(10**5), "CO2"))/1000
    tabla_propiedades.loc['7','Densidad (Kg/m^3)']=CP.PropsSI("D", "T", tabla_propiedades.loc['7','Temperatura (°C)']+273.15 , "P", presion_gascooler*(10**5), "CO2")
   
    tabla_propiedades.loc['6','Presión (bar)']=presion_gascooler
    tabla_propiedades.loc['6s','Presión (bar)']=presion_gascooler

    #R_isentropico=(0.707934084+0.0301499917*(tabla_propiedades.loc['1','Presión (bar)']*0.1)-0.0596514832*(presion_gascooler/tabla_propiedades.loc['1','Presión (bar)']))*100
    #R_volumetrico_baja_teorico=(1.30455467+0.00970194263*(tabla_propiedades.loc['1','Presión (bar)']*0.1)-0.0996564037*(presion_gascooler/tabla_propiedades.loc['1','Presión (bar)']))*100

    R_volumetrico_baja_teorico=16.6771332-0.01201859*presion_gascooler-0.24571796*tabla_propiedades.loc['1','Presión (bar)']+3.20332109*F-0.00191565*presion_gascooler**2-0.00219801*(tabla_propiedades.loc['1','Presión (bar)']**2)-0.02935512*(F**2)+0.00394487*presion_gascooler*tabla_propiedades.loc['1','Presión (bar)']-0.00015889*presion_gascooler*F+0.00468126*tabla_propiedades.loc['1','Presión (bar)']*F
    R_volumetrico_alta_teorico=(16.6771332-0.01201859*presion_gascooler-0.24571796*tabla_propiedades.loc['1','Presión (bar)']+3.20332109*F-0.00191565*presion_gascooler**2-0.00219801*(tabla_propiedades.loc['1','Presión (bar)']**2)-0.02935512*(F**2)+0.00394487*presion_gascooler*tabla_propiedades.loc['1','Presión (bar)']-0.00015889*presion_gascooler*F+0.00468126*tabla_propiedades.loc['1','Presión (bar)']*F)*(5.6/8)
    R_isentropico=20.4779885-0.08736845*presion_gascooler+1.02075047*tabla_propiedades.loc['1','Presión (bar)']+1.6838928*F-0.00394391*(presion_gascooler**2)-0.03363405*(tabla_propiedades.loc['1','Presión (bar)']**2)-0.01626644*(F**2)+0.01909573*presion_gascooler*tabla_propiedades.loc['1','Presión (bar)']+0.00315153*presion_gascooler*F-0.01128725*tabla_propiedades.loc['1','Presión (bar)']*F 
    

    def calcular(variables):
        p_intermedia_supuesto,mcc1_supuesto,mcc2_supuesto=variables

        #R_volumetrico_alta_teorico=(1.09386887+0.000763078811*(p_intermedia_supuesto*0.1)-0.0876745754*(tabla_propiedades.loc['1','Presión (bar)']*0.1)-0.0996564037*(presion_gascooler/tabla_propiedades.loc['1','Presión (bar)']))*100

        tabla_propiedades.loc['4','Presión (bar)']=p_intermedia_supuesto
        tabla_propiedades.loc['4s','Presión (bar)']=p_intermedia_supuesto
        tabla_propiedades.loc['5','Presión (bar)']=p_intermedia_supuesto
        tabla_propiedades.loc['8','Presión (bar)']=p_intermedia_supuesto
        tabla_propiedades.loc['9','Presión (bar)']=p_intermedia_supuesto
        tabla_propiedades.loc['11','Presión (bar)']=p_intermedia_supuesto
        tabla_propiedades.loc['12','Presión (bar)']=p_intermedia_supuesto
        tabla_propiedades.loc['14','Presión (bar)']=p_intermedia_supuesto

        tabla_propiedades.loc['3','Caudal másico (Kg/s)']=(R_volumetrico_baja_teorico/100)*mcc1_supuesto
        tabla_propiedades.loc['5','Caudal másico (Kg/s)']=(R_volumetrico_alta_teorico/100)*mcc2_supuesto

        tabla_propiedades.loc['3','Densidad (Kg/m^3)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']/((8*(R_volumetrico_baja_teorico/100)*F)/10**6)
        tabla_propiedades.loc['5','Densidad (Kg/m^3)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']/((5.6*(R_volumetrico_alta_teorico/100)*F)/10**6)

        tabla_propiedades.loc['3','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['3','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['3','Densidad (Kg/m^3)'], "CO2"))-273.15
        tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['3','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['3','Densidad (Kg/m^3)'], "CO2"))/1000
        tabla_propiedades.loc['3','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['3','Presión (bar)']*(10**5) , "D",tabla_propiedades.loc['3','Densidad (Kg/m^3)'], "CO2"))/1000
        tabla_propiedades.loc['3','Título de vapor']=None

        tabla_propiedades.loc['5','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D",tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))-273.15
        tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000
        tabla_propiedades.loc['5','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D",tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000
        tabla_propiedades.loc['5','Título de vapor']=None

        tabla_propiedades.loc['4s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']
        tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['4s','Presión (bar)']*(10**5) , "S",tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
        tabla_propiedades.loc['4s','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['4s','Presión (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
        tabla_propiedades.loc['4s','Caudal másico (Kg/s)']=0
        tabla_propiedades.loc['4s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",tabla_propiedades.loc['4s','Presión (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2")
        tabla_propiedades.loc['4s','Título de vapor']=None

        tabla_propiedades.loc['6s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']
        tabla_propiedades.loc['6s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['6s','Presión (bar)']*(10**5) , "S",tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
        tabla_propiedades.loc['6s','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['6s','Presión (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
        tabla_propiedades.loc['6s','Caudal másico (Kg/s)']=0
        tabla_propiedades.loc['6s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",tabla_propiedades.loc['6s','Presión (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2")
        tabla_propiedades.loc['6s','Título de vapor']=None

        tabla_propiedades.loc['4','Entalpía (kJ/Kg)']=tabla_propiedades.loc['3','Entalpía (kJ/Kg)']+(tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])/(R_isentropico/100)
        tabla_propiedades.loc['4','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['4','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))-273.15
        tabla_propiedades.loc['4','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",tabla_propiedades.loc['4','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2")
        tabla_propiedades.loc['4','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
        tabla_propiedades.loc['4','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['4','Presión (bar)']*(10**5) , "H",tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
        tabla_propiedades.loc['4','Título de vapor']=None

        tabla_propiedades.loc['6','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']
        tabla_propiedades.loc['7','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']
        tabla_propiedades.loc['8','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']

        tabla_propiedades.loc['6','Entalpía (kJ/Kg)']=tabla_propiedades.loc['5','Entalpía (kJ/Kg)']+(tabla_propiedades.loc['6s','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])/(R_isentropico/100)
        tabla_propiedades.loc['6','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['6','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['6','Entalpía (kJ/Kg)']*1000, "CO2"))-273.15
        tabla_propiedades.loc['6','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",tabla_propiedades.loc['6','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['6','Entalpía (kJ/Kg)']*1000, "CO2")
        tabla_propiedades.loc['6','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['6','Presión (bar)']*(10**5) , "H",tabla_propiedades.loc['6','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
        tabla_propiedades.loc['6','Título de vapor']=None

        tabla_propiedades.loc['8','Entalpía (kJ/Kg)']=tabla_propiedades.loc['7','Entalpía (kJ/Kg)']
        tabla_propiedades.loc['8','Título de vapor']=CP.PropsSI("Q", "P",tabla_propiedades.loc['8','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2")
        tabla_propiedades.loc['8','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['8','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2"))-273.15
        tabla_propiedades.loc['8','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",tabla_propiedades.loc['8','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2")
        tabla_propiedades.loc['8','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['8','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
        tabla_propiedades.loc['8','Título de vapor']=round(tabla_propiedades.loc['8','Título de vapor'],3)

        tabla_propiedades.loc['9','Título de vapor']=0.000
        tabla_propiedades.loc['9','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['9','Presión (bar)']*(10**5) , "Q",0, "CO2"))/1000
        tabla_propiedades.loc['9','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['9','Presión (bar)']*(10**5) , "Q",0, "CO2"))/1000
        tabla_propiedades.loc['9','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['9','Presión (bar)']*(10**5) , "Q",0, "CO2"))-273.15
        tabla_propiedades.loc['9','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",tabla_propiedades.loc['9','Presión (bar)']*(10**5) , "Q", 0, "CO2")
        tabla_propiedades.loc['9','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(1-tabla_propiedades.loc['8','Título de vapor'])

        tabla_propiedades.loc['1','Caudal másico (Kg/s)']=tabla_propiedades.loc['9','Caudal másico (Kg/s)']
        tabla_propiedades.loc['2','Caudal másico (Kg/s)']=tabla_propiedades.loc['9','Caudal másico (Kg/s)']

        tabla_propiedades.loc['10','Entalpía (kJ/Kg)']=tabla_propiedades.loc['9','Entalpía (kJ/Kg)']
        tabla_propiedades.loc['10','Título de vapor']=CP.PropsSI("Q", "P",tabla_propiedades.loc['10','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2")
        tabla_propiedades.loc['10','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['10','Presión (bar)']*(10**5) , "H",tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
        tabla_propiedades.loc['10','Temperatura (°C)']=tabla_propiedades.loc['1','Temperatura (°C)']
        tabla_propiedades.loc['10','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",tabla_propiedades.loc['10','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2")
        tabla_propiedades.loc['10','Título de vapor']=round(tabla_propiedades.loc['10','Título de vapor'],3)
        tabla_propiedades.loc['10','Caudal másico (Kg/s)']=tabla_propiedades.loc['9','Caudal másico (Kg/s)']

        tabla_propiedades.loc['11','Presión (bar)']=tabla_propiedades.loc['11','Presión (bar)']
        tabla_propiedades.loc['11','Título de vapor']=1.000
        tabla_propiedades.loc['11','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['11','Presión (bar)']*(10**5) , "Q",1, "CO2"))/1000
        tabla_propiedades.loc['11','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['11','Presión (bar)']*(10**5) , "Q",1, "CO2"))/1000
        tabla_propiedades.loc['11','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['11','Presión (bar)']*(10**5) , "Q",1, "CO2"))-273.15
        tabla_propiedades.loc['11','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",tabla_propiedades.loc['11','Presión (bar)']*(10**5) , "Q", 1, "CO2")
        tabla_propiedades.loc['11','Caudal másico (Kg/s)']=tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(tabla_propiedades.loc['8','Título de vapor'])

        tabla_propiedades.loc['13','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']-tabla_propiedades.loc['2','Caudal másico (Kg/s)']
        tabla_propiedades.loc['12','Caudal másico (Kg/s)']=tabla_propiedades.loc['13','Caudal másico (Kg/s)']

        tabla_propiedades.loc['12','Entalpía (kJ/Kg)']=tabla_propiedades.loc['11','Entalpía (kJ/Kg)']
        tabla_propiedades.loc['12','Temperatura (°C)']=tabla_propiedades.loc['11','Temperatura (°C)']
        tabla_propiedades.loc['12','Título de vapor']=tabla_propiedades.loc['11','Título de vapor']
        tabla_propiedades.loc['12','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['11','Entropía (kJ/Kg·K)']
        tabla_propiedades.loc['12','Densidad (Kg/m^3)']=tabla_propiedades.loc['11','Densidad (Kg/m^3)']

        tabla_propiedades.loc['14','Entalpía (kJ/Kg)']=tabla_propiedades.loc['11','Entalpía (kJ/Kg)']
        tabla_propiedades.loc['14','Temperatura (°C)']=tabla_propiedades.loc['11','Temperatura (°C)']
        tabla_propiedades.loc['14','Título de vapor']=tabla_propiedades.loc['11','Título de vapor']
        tabla_propiedades.loc['14','Entalpía (kJ/Kg)']=tabla_propiedades.loc['11','Entalpía (kJ/Kg)']
        tabla_propiedades.loc['14','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['11','Entropía (kJ/Kg·K)']
        tabla_propiedades.loc['14','Densidad (Kg/m^3)']=tabla_propiedades.loc['11','Densidad (Kg/m^3)']

        tabla_propiedades.loc['13','Entalpía (kJ/Kg)']=tabla_propiedades.loc['11','Entalpía (kJ/Kg)']
        tabla_propiedades.loc['13','Temperatura (°C)']=tabla_propiedades.loc['1','Temperatura (°C)']
        tabla_propiedades.loc['13','Título de vapor']=CP.PropsSI("Q", "P",tabla_propiedades.loc['13','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['11','Entalpía (kJ/Kg)']*1000, "CO2")
        tabla_propiedades.loc['13','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['13','Presión (bar)']*(10**5) , "H",tabla_propiedades.loc['11','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
        tabla_propiedades.loc['13','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",tabla_propiedades.loc['13','Presión (bar)']*(10**5) , "H", tabla_propiedades.loc['11','Entalpía (kJ/Kg)']*1000, "CO2")
        tabla_propiedades.loc['13','Título de vapor']=round(tabla_propiedades.loc['13','Título de vapor'],3)

        tabla_propiedades.loc['14','Caudal másico (Kg/s)']=tabla_propiedades.loc['11','Caudal másico (Kg/s)']-tabla_propiedades.loc['13','Caudal másico (Kg/s)']

        #Objetivos
        #error_caudal_1=abs(tabla_propiedades.loc['2','Caudal másico (Kg/s)']-tabla_propiedades.loc['3','Caudal másico (Kg/s)'])
        error_entalpia_1=abs(tabla_propiedades.loc['2','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])
        #error_caudal_2=abs(tabla_propiedades.loc['11','Caudal másico (Kg/s)']-tabla_propiedades.loc['14','Caudal másico (Kg/s)'])
        error_caudal_3=abs(tabla_propiedades.loc['5','Caudal másico (Kg/s)']-(tabla_propiedades.loc['14','Caudal másico (Kg/s)']+tabla_propiedades.loc['4','Caudal másico (Kg/s)']))
        error_entalpia_2=abs(tabla_propiedades.loc['5','Caudal másico (Kg/s)']*tabla_propiedades.loc['5','Entalpía (kJ/Kg)']-(tabla_propiedades.loc['14','Caudal másico (Kg/s)']*tabla_propiedades.loc['14','Entalpía (kJ/Kg)']-tabla_propiedades.loc['4','Caudal másico (Kg/s)']*tabla_propiedades.loc['4','Entalpía (kJ/Kg)']))

        error_caudal=abs(tabla_propiedades.loc['13','Caudal másico (Kg/s)'])

        #Combinación de objetivos (método de suma ponderada)
        #peso_caudal_1 = 0.2
        peso_entalpia_1 = 0.6
        #peso_caudal_2 = 0.2
        peso_caudal_3 = 0.2
        peso_entalpia_2=0.2

        peso_caudal=1000


        #error_caudal_1*peso_caudal_1+error_entalpia_1*peso_entalpia_1+error_caudal_2*peso_caudal_2+error_caudal_3*peso_caudal_3+error_entalpia_2*peso_entalpia_2
        return  error_caudal*peso_caudal+error_entalpia_1*peso_entalpia_1+error_caudal_3*peso_caudal_3+error_entalpia_2*peso_entalpia_2
    
    resultado = minimize(calcular,
    x0=[50,0.01,0.02],
    bounds=[(45,60),(0.015, 0.025),(0.02, 0.035)],
    method='L-BFGS-B',
    options={'ftol': 1e-15}    )

    columnas=['Temperatura (°C)','Presión (bar)','Entalpía (kJ/Kg)','Entropía (kJ/Kg·K)','Densidad (Kg/m^3)']
    tabla_propiedades[columnas] = tabla_propiedades[columnas].apply(pd.to_numeric, errors='coerce')
    tabla_propiedades[columnas] = tabla_propiedades[columnas].round(3)
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

    tabla_propiedades_balance.loc['Potencia frigorífica (evaporadores)','Valores']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['1','Entalpía (kJ/Kg)']-tabla_propiedades.loc['10','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['2','Entalpía (kJ/Kg)']-tabla_propiedades.loc['1','Entalpía (kJ/Kg)'])
    tabla_propiedades_balance.loc['Potencia ideal (compresor)','Valores']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']*(tabla_propiedades.loc['4','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])
    tabla_propiedades_balance.loc['Potencia cedida (gas-cooler)','Valores']=tabla_propiedades.loc['6','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['7','Entalpía (kJ/Kg)'])
    tabla_propiedades_balance.loc['Consumo eléctrico (compresor)','Valores']=tabla_propiedades_balance.loc['Potencia ideal (compresor)','Valores']/0.9
    tabla_propiedades_balance.loc['COP (EER)','Valores']=tabla_propiedades_balance.loc['Potencia frigorífica (evaporadores)','Valores']/tabla_propiedades_balance.loc['Consumo eléctrico (compresor)','Valores']
    tabla_propiedades_balance.loc['COP (BC)','Valores']=tabla_propiedades_balance.loc['Potencia cedida (gas-cooler)','Valores']/tabla_propiedades_balance.loc['Consumo eléctrico (compresor)','Valores']

    st.dataframe(tabla_propiedades_balance,height=245,use_container_width=True,hide_index=False)

    #Análisis compresor
    st.markdown("<br>", unsafe_allow_html=True) 
        
    st.markdown("<p style='font-size: 17px;'><strong>Análisis compresor</strong></p>", unsafe_allow_html=True)
  
    tabla_propiedades_compresor=pd.DataFrame(columns=['Valores','Unidades'],index=['Velocidad de giro','Capacidad de desplazamiento (primera etapa)','Capacidad de desplazamiento (segunda etapa)','Flujo másico geométrico (primera etapa)','Flujo másico geométrico (segunda etapa)','Flujo másico (primera etapa)','Flujo másico (segunda etapa)','Rendimiento isentrópico (primera etapa)','Rendimiento isentrópico (segunda etapa)','Rendimiento volumétrico (primera etapa)','Rendimiento volumétrico (segunda etapa)','Rendimiento electromecánico (supuesto)','Consumo de energía isentrópica ideal','Consumo eléctrico'])
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
    tabla_propiedades_compresor.loc['Rendimiento electromecánico (supuesto)','Unidades']='%' 
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
    tabla_propiedades_compresor.loc['Consumo eléctrico','Valores']=tabla_propiedades_compresor.loc['Consumo de energía isentrópica ideal','Valores']/0.9
    tabla_propiedades_compresor.loc['Rendimiento electromecánico (supuesto)','Valores']=90

    st.dataframe(tabla_propiedades_compresor,height=400,use_container_width=True,hide_index=False)

#Análisis evaporadores
    #st.markdown("<br>", unsafe_allow_html=True) 
    #    
    #st.markdown("<p style='font-size: 17px;'><strong>Análisis evaporadores</strong></p>", unsafe_allow_html=True)
  #
    #tabla_propiedades_evaporadores=pd.DataFrame(columns=['Valores','Unidades'],index=['Potencia (ventiladores)','Velocidad de giro (ventiladores)','Caudal (aire - total)','Temperatura entrada (aire - evaporador 1)','Temperatura salida (aire - evaporador 1)','Temperatura entrada (aire - evaporador 2)','Temperatura salida (aire - evaporador 2)','Transferencia térmica (aire - evaporador 1)','Transferencia térmica (aire - evaporador 2)','Transferencia térmica (aire - total)','Flujo másico (refrigerante - total)','Transferencia térmica (refrigerante - total)','Efectividad (evaporador 1)','Efectividad (evaporador 2)','Discrepancia térmica (evaporador 1)','Discrepancia térmica (evaporador 2)','Salto térmico (entrada - evaporador 1)','Salto térmico (salida - evaporador 1)','Salto térmico (entrada - evaporador 2)','Salto térmico (salida - evaporador 2)','Sobrecalentamiento (evaporador 1)','Sobrecalentamiento (evaporador 2)'])
    #tabla_propiedades_evaporadores.index.name = "Variables"
    #tabla_propiedades_evaporadores.loc['Potencia (ventiladores)','Unidades']='%'
    #tabla_propiedades_evaporadores.loc['Velocidad de giro (ventiladores)','Unidades']='rpm'
    #tabla_propiedades_evaporadores.loc['Caudal (aire - total)','Unidades']='m^3/s'
    #tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 1)','Unidades']='°C'
    #tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 1)','Unidades']='°C'
    #tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 2)','Unidades']='°C'
    #tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 2)','Unidades']='°C'
    #tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 1)','Unidades']='kW'
    #tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 2)','Unidades']='kW'
    #tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - total)','Unidades']='kW'
    #tabla_propiedades_evaporadores.loc['Flujo másico (refrigerante - total)','Unidades']='Kg/s'
    #tabla_propiedades_evaporadores.loc['Transferencia térmica (refrigerante - total)','Unidades']='kW'
    #tabla_propiedades_evaporadores.loc['Efectividad (evaporador 1)','Unidades']='%'
    #tabla_propiedades_evaporadores.loc['Efectividad (evaporador 2)','Unidades']='%'
    #tabla_propiedades_evaporadores.loc['Discrepancia térmica (evaporador 1)','Unidades']='%'
    #tabla_propiedades_evaporadores.loc['Discrepancia térmica (evaporador 2)','Unidades']='%'
    #tabla_propiedades_evaporadores.loc['Salto térmico (entrada - evaporador 1)','Unidades']='K'
    #tabla_propiedades_evaporadores.loc['Salto térmico (salida - evaporador 1)','Unidades']='K'
    #tabla_propiedades_evaporadores.loc['Salto térmico (entrada - evaporador 2)','Unidades']='K'
    #tabla_propiedades_evaporadores.loc['Salto térmico (salida - evaporador 2)','Unidades']='K'
    #tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 1)','Unidades']='K'
    #tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 2)','Unidades']='K'
#
    #tabla_propiedades_evaporadores.loc['Potencia (ventiladores)','Valores']=100
    #tabla_propiedades_evaporadores.loc['Velocidad de giro (ventiladores)','Valores']=2600
    #tabla_propiedades_evaporadores.loc['Caudal (aire - total)','Valores']=0.292
    #tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 1)','Valores']=media['Temperatura camara (evaporador 1) (°C)']
    #tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 1)','Valores']=media['Temperatura desescarche (evaporador 1) (°C)']
    #tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 2)','Valores']=media['Temperatura camara (evaporador 2) (°C)']
    #tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 2)','Valores']=media['Temperatura desescarche (evaporador 2) (°C)']
    #tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 1)','Valores']=(0.292/2)*1.344*1.006*(media['Temperatura camara (evaporador 1) (°C)']-media['Temperatura desescarche (evaporador 1) (°C)'])
    #tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 2)','Valores']=(0.292/2)*1.344*1.006*(media['Temperatura camara (evaporador 2) (°C)']-media['Temperatura desescarche (evaporador 2) (°C)'])
    #tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - total)','Valores']=tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 1)','Valores']+tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 2)','Valores']
    #tabla_propiedades_evaporadores.loc['Flujo másico (refrigerante - total)','Valores']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']
    #tabla_propiedades_evaporadores.loc['Transferencia térmica (refrigerante - total)','Valores']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['1','Entalpía (kJ/Kg)']-tabla_propiedades.loc['10','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['2','Entalpía (kJ/Kg)']-tabla_propiedades.loc['1','Entalpía (kJ/Kg)'])
    #tabla_propiedades_evaporadores.loc['Efectividad (evaporador 1)','Valores']=round((media['Temperatura camara (evaporador 1) (°C)']-media['Temperatura desescarche (evaporador 1) (°C)'])*100/(media['Temperatura camara (evaporador 1) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),2)
    #tabla_propiedades_evaporadores.loc['Efectividad (evaporador 2)','Valores']=round((media['Temperatura camara (evaporador 2) (°C)']-media['Temperatura desescarche (evaporador 2) (°C)'])*100/(media['Temperatura camara (evaporador 2) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),2)
    #tabla_propiedades_evaporadores.loc['Discrepancia térmica (evaporador 1)','Valores']=round(tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 1)','Valores']*100/(tabla_propiedades_evaporadores.loc['Transferencia térmica (refrigerante - total)','Valores']/2),2)
    #tabla_propiedades_evaporadores.loc['Discrepancia térmica (evaporador 2)','Valores']=round(tabla_propiedades_evaporadores.loc['Transferencia térmica (aire - evaporador 2)','Valores']*100/(tabla_propiedades_evaporadores.loc['Transferencia térmica (refrigerante - total)','Valores']/2),2)
    #tabla_propiedades_evaporadores.loc['Salto térmico (entrada - evaporador 1)','Valores']=tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 1)','Valores']-tabla_propiedades.loc['2','Temperatura (°C)']
    #tabla_propiedades_evaporadores.loc['Salto térmico (salida - evaporador 1)','Valores']=tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 1)','Valores']-tabla_propiedades.loc['1','Temperatura (°C)']
    #tabla_propiedades_evaporadores.loc['Salto térmico (entrada - evaporador 2)','Valores']=tabla_propiedades_evaporadores.loc['Temperatura entrada (aire - evaporador 2)','Valores']-tabla_propiedades.loc['2','Temperatura (°C)']
    #tabla_propiedades_evaporadores.loc['Salto térmico (salida - evaporador 2)','Valores']=tabla_propiedades_evaporadores.loc['Temperatura salida (aire - evaporador 2)','Valores']-tabla_propiedades.loc['1','Temperatura (°C)']
    #if ('Recalentamiento (valvula expansion 1) (K)' in media.index) and ('Recalentamiento (valvula expansion 2) (K)' in media.index):
    #    tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 1)','Valores']=round(media['Recalentamiento (valvula expansion 1) (K)'],3)
    #    tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 2)','Valores']=round(media['Recalentamiento (valvula expansion 2) (K)'],3)
    #else:
    #    tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 1)','Valores']=round(abs(tabla_propiedades.loc['2','Temperatura (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),3)
    #    tabla_propiedades_evaporadores.loc['Sobrecalentamiento (evaporador 2)','Valores']=round(abs(tabla_propiedades.loc['2','Temperatura (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),3)
    #
    #st.dataframe(tabla_propiedades_evaporadores,height=400,use_container_width=True,hide_index=False)
#