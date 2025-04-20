import requests # Peticiones HTTP
from datetime import datetime, timedelta      
import pandas as pd
import matplotlib.pyplot as plt     
import numpy as np
import streamlit as st
import altair as alt
from time import sleep
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont

#Importación de funciones API
from API import request_login
from API import make_charts_request
from API import process_charts_response

def datos_continuo(lista_variables,tipo_grafico,intervalo_visualizacion):

    #Configuración API
    USERNAME = "juancarlosperez"
    PASSWORD = "Jcjmtj_12345"

    #Datos de la instalación y el control
    DEVICE_UUID = "073c3e1b-32bf-419f-b36c-2b27d91979e4" # UUID instalación
    CONTROL_UUID_analizador_redes = "266fabeb-3818-4509-b2da-894440c93987" # UUID control
    CONTROL_UUID_evaporador_04 = "f203037b-c873-43f1-b640-34a7bea70e4b" # UUID control
    CONTROL_UUID_valvula_expansion_05 = "9f8b564a-bbfb-4515-aedb-3af2007a9c86" # UUID control
    CONTROL_UUID_evaporador_06 = "5a51de17-461e-4c0b-8f45-e791bf42aa9a" # UUID control
    CONTROL_UUID_valvula_expansion_07 = "f64e5e27-f764-43a3-8a32-9c0f3ee1623b" # UUID control
    CONTROL_UUID_equipo = "d31de114-9cff-4b09-8bc3-7b9ee4b48194" # UUID control

    ENTITIES_analizador_redes = [ # Variables a consultar
          {
            "id": 4555619,
            "name": "Potencia total (W)"
          },
          {
            "id": 4555627,
            "name": "Energia total (kWh)"
          }
    ]

    ENTITIES_evaporador_04 = [ # Variables a consultar
          {
            "id": 4555662,
            "name": "Temperatura camara (evaporador 1) (°C)"
          },
          {
            "id": 4555666,
            "name": "Temperatura desescarche (evaporador 1) (°C)"
          },
          {
            "id": 4555750,
            "name": "Rele desescarche (evaporador 1) (on/off)"     
          },
          {
            "id": 4555751,
            "name": "Rele ventilador (evaporador 1) (on/off)"        
          },
          {
            "id": 4555752,
            "name": "Rele valvula (evaporador 1) (on/off)"          
          },
          {
            "id": 4555744,
            "name": "Estado desescarche (evaporador 1) (on/off)"           
          },
          {
            "id": 4555749,
            "name": "Estado dispositivo (evaporador 1) (on/off)"       
          }
    ]
    ENTITIES_valvula_expansion_05 = [ # Variables a consultar
          {
            "id": 4555913,
            "name": "Presion de baja (valvula expansion 1) (bar)"
          },
          {
            "id": 4555914,
            "name": "Temperatura aspiracion (valvula expansion 1) (°C)"
          },
          {
            "id": 4555922,
            "name": "Recalentamiento (valvula expansion 1) (K)"     
          },
          {
            "id": 4555929,
            "name": "Apertura valvula (valvula expansion 1) (%)"   
          },
          {
            "id": 4555974,
            "name": "Estado valvula (valvula expansion 1) (on/off)"   
          }    
    ]
    
    ENTITIES_evaporador_06 = [ # Variables a consultar
          {
            "id": 4556044,
            "name": "Temperatura camara (evaporador 2) (°C)"
          },
          {
            "id": 4556048,
            "name": "Temperatura desescarche (evaporador 2) (°C)"
          },
          {
            "id": 4556132,
            "name": "Rele desescarche (evaporador 2) (on/off)"     
          },
          {
            "id": 4556133,
            "name": "Rele ventilador (evaporador 2) (on/off)"        
          },
          {
            "id": 4556134,
            "name": "Rele valvula (evaporador 2) (on/off)"          
          },
          {
            "id": 4556126,
            "name": "Estado desescarche (evaporador 2) (on/off)"           
          },
          {
            "id": 4556131,
            "name": "Estado dispositivo (evaporador 2) (on/off)"       
          }
    ]
    
    
    ENTITIES_valvula_expansion_07 = [ # Variables a consultar
          {
            "id": 4556423,
            "name": "Presion de baja (valvula expansion 2) (bar)"
          },
          {
            "id": 4556424,
            "name": "Temperatura aspiracion (valvula expansion 2) (°C)"
          },
          {
            "id": 4556432,
            "name": "Recalentamiento (valvula expansion 2) (K)"     
          },
          {
            "id": 4556439,
            "name": "Apertura valvula (valvula expansion 2) (%)"   
          },
          {
            "id": 4556484,
            "name": "Estado valvula (valvula expansion 2) (on/off)"   
          }    
    ]
    
    ENTITIES_equipo = [ # Variables a consultar
          {
            "id": 5368851,
            "name": "Presion evaporacion (bar)"
          },
          {
            "id": 5368856,
            "name": "Temperatura evaporacion (°C)"
          },
          {
            "id": 5368850,
            "name": "Presion condensacion (bar)"
          },
          {
            "id": 5368854,
            "name": "Temperatura condensacion (°C)"
          },
          {
            "id": 5368852,
            "name": "Presion deposito (bar)"
          },
          {
            "id": 5369115,
            "name": "Temperatura deposito (°C)"
          },
          {
            "id": 5368858,
            "name": "Temperatura exterior (°C)"
          },
          {
            "id": 5368859,
            "name": "Temperatura salida gas cooler (°C)"
          },
          {
            "id": 5368853,
            "name": "Temperatura aspiracion (°C)"
          },
          {
            "id": 5368855,
            "name": "Temperatura descarga (°C)"
          },
          {
            "id": 5369112,
            "name": "Temperatura liquido (°C)"
          },
          {
            "id": 5368727,
            "name": "Potencia compresor (%)"
          },
          {
            "id": 5368730,
            "name": "Potencia ventilador gas-cooler (%)"
          },      
          {
            "id": 5368728,
            "name": "Apertura valvula by-pass (%)"
          },
          {
            "id": 5368729,
            "name": "Apertura valvula alta presion (%)"       
          },
          {
            "id": 5368947,
            "name": "Rele compresor (on/off)"     
          }
    ]

    #Token
    TOKEN = request_login(USERNAME, PASSWORD)

    # Obtener la fecha y hora actual
    ahora = datetime.now()
    ahora = ahora -timedelta(minutes=60)
    fecha_ahora = ahora.strftime("%H:%M_%Y%m%d")
    antes = ahora - timedelta(minutes=intervalo_visualizacion+1)
    fecha_antes=antes.strftime("%H:%M_%Y%m%d")

    #Intervalo de tiempo para llamar al servidor
    FROM_STR = fecha_antes
    UNTIL_STR = fecha_ahora
    INTERVAL = 60 # En segundos

    #Petición de histórico de datos al servidor y posterior procesamiento 
    response_analizador_redes = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_analizador_redes, ENTITIES_analizador_redes, FROM_STR, UNTIL_STR, INTERVAL)
    df_analizador_redes = process_charts_response(DEVICE_UUID, CONTROL_UUID_analizador_redes, ENTITIES_analizador_redes, response_analizador_redes)

    response_evaporador_04 = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_evaporador_04, ENTITIES_evaporador_04, FROM_STR, UNTIL_STR, INTERVAL)
    df_evaporador_04 = process_charts_response(DEVICE_UUID, CONTROL_UUID_evaporador_04, ENTITIES_evaporador_04, response_evaporador_04)

    response_valvula_expansion_05 = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_valvula_expansion_05, ENTITIES_valvula_expansion_05, FROM_STR, UNTIL_STR, INTERVAL)
    df_valvula_expansion_05 = process_charts_response(DEVICE_UUID, CONTROL_UUID_valvula_expansion_05, ENTITIES_valvula_expansion_05, response_valvula_expansion_05)

    response_evaporador_06 = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_evaporador_06, ENTITIES_evaporador_06, FROM_STR, UNTIL_STR, INTERVAL)
    df_evaporador_06 = process_charts_response(DEVICE_UUID, CONTROL_UUID_evaporador_06, ENTITIES_evaporador_06, response_evaporador_06)

    response_valvula_expansion_07 = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_valvula_expansion_07, ENTITIES_valvula_expansion_07, FROM_STR, UNTIL_STR, INTERVAL)
    df_valvula_expansion_07 = process_charts_response(DEVICE_UUID, CONTROL_UUID_valvula_expansion_07, ENTITIES_valvula_expansion_07, response_valvula_expansion_07)

    response_equipo = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_equipo, ENTITIES_equipo, FROM_STR, UNTIL_STR, INTERVAL)
    df_equipo = process_charts_response(DEVICE_UUID, CONTROL_UUID_equipo, ENTITIES_equipo, response_equipo)

 
    #PREPROCESADO

    #Establecer el índice correcto

    df_analizador_redes.index = df_analizador_redes.index.tz_localize(None)
    df_analizador_redes.index=df_analizador_redes.index.floor('min')
    inicio_df_analizador_redes=df_analizador_redes.index[0]
    fin_df_analizador_redes=df_analizador_redes.index[-1]
    indice_nuevo_df_analizador_redes=pd.date_range(start=inicio_df_analizador_redes,end=fin_df_analizador_redes,freq='min')
    df_analizador_redes=df_analizador_redes.reindex(indice_nuevo_df_analizador_redes)

    df_evaporador_04.index = df_evaporador_04.index.tz_localize(None)
    df_evaporador_04.index=df_evaporador_04.index.floor('min')
    inicio_df_evaporador_04=df_evaporador_04.index[0]
    fin_df_evaporador_04=df_evaporador_04.index[-1]
    indice_nuevo_df_evaporador_04=pd.date_range(start=inicio_df_evaporador_04,end=fin_df_evaporador_04,freq='min')
    df_evaporador_04=df_evaporador_04.reindex(indice_nuevo_df_evaporador_04)

    df_valvula_expansion_05.index = df_valvula_expansion_05.index.tz_localize(None)
    df_valvula_expansion_05.index=df_valvula_expansion_05.index.floor('min')
    inicio_df_valvula_expansion_05=df_valvula_expansion_05.index[0]
    fin_df_valvula_expansion_05=df_valvula_expansion_05.index[-1]
    indice_nuevo_df_valvula_expansion_05=pd.date_range(start=inicio_df_valvula_expansion_05,end=fin_df_valvula_expansion_05,freq='min')
    df_valvula_expansion_05=df_valvula_expansion_05.reindex(indice_nuevo_df_valvula_expansion_05)

    df_evaporador_06.index = df_evaporador_06.index.tz_localize(None)
    df_evaporador_06.index=df_evaporador_06.index.floor('min')
    inicio_df_evaporador_06=df_evaporador_06.index[0]
    fin_df_evaporador_06=df_evaporador_06.index[-1]
    indice_nuevo_df_evaporador_06=pd.date_range(start=inicio_df_evaporador_06,end=fin_df_evaporador_06,freq='min')
    df_evaporador_06=df_evaporador_06.reindex(indice_nuevo_df_evaporador_06)

    df_valvula_expansion_07.index = df_valvula_expansion_07.index.tz_localize(None)
    df_valvula_expansion_07.index=df_valvula_expansion_07.index.floor('min')
    inicio_df_valvula_expansion_07=df_valvula_expansion_07.index[0]
    fin_df_valvula_expansion_07=df_valvula_expansion_07.index[-1]
    indice_nuevo_df_valvula_expansion_07=pd.date_range(start=inicio_df_valvula_expansion_07,end=fin_df_valvula_expansion_07,freq='min')
    df_valvula_expansion_07=df_valvula_expansion_07.reindex(indice_nuevo_df_valvula_expansion_07)

    df_equipo.index = df_equipo.index.tz_localize(None)
    df_equipo.index=df_equipo.index.floor('min')
    inicio_df_equipo=df_equipo.index[0]
    fin_df_equipo=df_equipo.index[-1]
    indice_nuevo_df_equipo=pd.date_range(start=inicio_df_equipo,end=fin_df_equipo,freq='min')
    df_equipo=df_equipo.reindex(indice_nuevo_df_equipo)

    #Rellenado de datos omitidos

    columnas_no_vacias = df_analizador_redes.columns[~df_analizador_redes.isna().all()].tolist()
    df_analizador_redes[columnas_no_vacias]=df_analizador_redes[columnas_no_vacias].interpolate()
    df_analizador_redes[columnas_no_vacias]=df_analizador_redes[columnas_no_vacias].bfill()
    df_analizador_redes[columnas_no_vacias]=df_analizador_redes[columnas_no_vacias].ffill()
    df_analizador_redes[columnas_no_vacias]=df_analizador_redes[columnas_no_vacias].round(2)

    columnas_no_vacias = df_evaporador_04.columns[~df_evaporador_04.isna().all()].tolist()
    df_evaporador_04[columnas_no_vacias]=df_evaporador_04[columnas_no_vacias].interpolate()
    df_evaporador_04[columnas_no_vacias]=df_evaporador_04[columnas_no_vacias].bfill()
    df_evaporador_04[columnas_no_vacias]=df_evaporador_04[columnas_no_vacias].ffill()
    df_evaporador_04[columnas_no_vacias]=df_evaporador_04[columnas_no_vacias].round(2)

    columnas_no_vacias = df_valvula_expansion_05.columns[~df_valvula_expansion_05.isna().all()].tolist()
    df_valvula_expansion_05[columnas_no_vacias]=df_valvula_expansion_05[columnas_no_vacias].interpolate()
    df_valvula_expansion_05[columnas_no_vacias]=df_valvula_expansion_05[columnas_no_vacias].bfill()
    df_valvula_expansion_05[columnas_no_vacias]=df_valvula_expansion_05[columnas_no_vacias].ffill()
    df_valvula_expansion_05[columnas_no_vacias]=df_valvula_expansion_05[columnas_no_vacias].round(2)

    columnas_no_vacias = df_evaporador_06.columns[~df_evaporador_06.isna().all()].tolist()
    df_evaporador_06[columnas_no_vacias]=df_evaporador_06[columnas_no_vacias].interpolate()
    df_evaporador_06[columnas_no_vacias]=df_evaporador_06[columnas_no_vacias].bfill()
    df_evaporador_06[columnas_no_vacias]=df_evaporador_06[columnas_no_vacias].ffill()
    df_evaporador_06[columnas_no_vacias]=df_evaporador_06[columnas_no_vacias].round(2)

    columnas_no_vacias = df_valvula_expansion_07.columns[~df_valvula_expansion_07.isna().all()].tolist()
    df_valvula_expansion_07[columnas_no_vacias]=df_valvula_expansion_07[columnas_no_vacias].interpolate()
    df_valvula_expansion_07[columnas_no_vacias]=df_valvula_expansion_07[columnas_no_vacias].bfill()
    df_valvula_expansion_07[columnas_no_vacias]=df_valvula_expansion_07[columnas_no_vacias].ffill()
    df_valvula_expansion_07[columnas_no_vacias]=df_valvula_expansion_07[columnas_no_vacias].round(2)

    columnas_no_vacias = df_equipo.columns[~df_equipo.isna().all()].tolist()
    df_equipo[columnas_no_vacias]=df_equipo[columnas_no_vacias].interpolate()
    df_equipo[columnas_no_vacias]=df_equipo[columnas_no_vacias].bfill()
    df_equipo[columnas_no_vacias]=df_equipo[columnas_no_vacias].ffill()
    df_equipo[columnas_no_vacias]=df_equipo[columnas_no_vacias].round(2)

    #Concatenar los dataframe que tienen columnas seleccionadas
    df_ampliado=pd.concat([df_analizador_redes,df_equipo,df_evaporador_04,df_valvula_expansion_05,df_evaporador_06,df_valvula_expansion_07],axis=1)
    df_ampliado=df_ampliado[lista_variables]
    variables_analogicas=["Potencia total (W)","Energia total (kWh)","Temperatura camara (evaporador 1) (°C)","Temperatura desescarche (evaporador 1) (°C)","Presion de baja (valvula expansion 1) (bar)","Temperatura aspiracion (valvula expansion 1) (°C)","Recalentamiento (valvula expansion 1) (K)","Apertura valvula (valvula expansion 1) (%)","Temperatura camara (evaporador 2) (°C)","Temperatura desescarche (evaporador 2) (°C)","Presion de baja (valvula expansion 2) (bar)","Temperatura aspiracion (valvula expansion 2) (°C)","Recalentamiento (valvula expansion 2) (K)","Apertura valvula (valvula expansion 2) (%)",'Presion evaporacion (bar)','Temperatura evaporacion (°C)',"Presion condensacion (bar)","Temperatura condensacion (°C)","Presion deposito (bar)","Temperatura deposito (°C)","Temperatura exterior (°C)","Temperatura salida gas cooler (°C)","Temperatura aspiracion (°C)","Temperatura descarga (°C)","Temperatura liquido (°C)","Potencia compresor (%)","Potencia ventilador gas-cooler (%)","Apertura valvula by-pass (%)","Apertura valvula alta presion (%)"]
    variables_digitales=["Rele desescarche (evaporador 1) (on/off)","Rele ventilador (evaporador 1) (on/off)","Rele valvula (evaporador 1) (on/off)","Estado desescarche (evaporador 1) (on/off)","Estado dispositivo (evaporador 1) (on/off)","Estado valvula (valvula expansion 1) (on/off)","Rele desescarche (evaporador 2) (on/off)","Rele ventilador (evaporador 2) (on/off)","Rele valvula (evaporador 2) (on/off)","Estado desescarche (evaporador 2) (on/off)","Estado dispositivo (evaporador 2) (on/off)","Estado valvula (valvula expansion 2) (on/off)","Rele compresor (on/off)"]
    lista_variables_analogicas=list(set(variables_analogicas) & set(lista_variables))
    lista_variables_digitales=list(set(variables_digitales) & set(lista_variables))
    df_ampliado_analogico=df_ampliado[lista_variables_analogicas]
    df_ampliado_digital=df_ampliado[lista_variables_digitales]
    df_ampliado_scada=pd.concat([df_ampliado_analogico,df_ampliado_digital],axis=1)
    df_ampliado_tabla=df_ampliado_scada
    df_ampliado_tabla.index = df_ampliado_tabla.index.strftime('%H:%M')


    if 'Tabla' in tipo_grafico:
        st.markdown("<br>", unsafe_allow_html=True) 
        #Información
        st.markdown("<p style='font-size: 17px;'><strong>Tabla</strong></p>", unsafe_allow_html=True)
##
        tabla_placeholder = st.empty()  # Placeholder para la tabla
        # Inicializar un DataFrame vacío para la tabla
        tabla_datos = pd.DataFrame(columns=lista_variables)
        tabla_datos.index.name = 'Hora'
##
        tabla_datos = df_ampliado_scada.copy()
        tabla_datos.index = df_ampliado_tabla.index
##
        # Mostrar la tabla actualizada
        tabla_placeholder.dataframe(tabla_datos,use_container_width=True)




    if 'Scada' in tipo_grafico:

        st.markdown("<br>", unsafe_allow_html=True) 
        #Información
        st.markdown("<p style='font-size: 17px;'><strong>Scada</strong></p>", unsafe_allow_html=True)
 
        # Cargar la imagen    
        imagen = Image.open("imagenes/scada.png")  # Cambia la ruta a tu imagen
        draw = ImageDraw.Draw(imagen)

        # Definir las posiciones donde se mostrarán los datos
        posiciones = {
        "Temperatura evaporacion (°C)": (230, 250),
        'Presion evaporacion (bar)': (230,566),
        'Presion condensacion (bar)': (1160,45),
        'Temperatura condensacion (°C)': (1030,2.5),
        'Presion deposito (bar)': (805,220),
        'Temperatura deposito (°C)': (990,220),
        'Temperatura exterior (°C)': (236,100),
        'Temperatura salida gas cooler (°C)': (722,50),
        'Temperatura aspiracion (°C)': (1030,285),
        'Temperatura descarga (°C)': (1190,140),
        'Temperatura liquido (°C)': (725,470),
        'Potencia compresor (%)': (1190,205),
        'Potencia ventilador gas-cooler (%)': (903,155),
        'Apertura valvula by-pass (%)': (850,325),
        'Apertura valvula alta presion (%)': (732,135),
        'Rele compresor (on/off)': (1165,530),
        'Temperatura camara (evaporador 1) (°C)': (17,185),
        'Temperatura desescarche (evaporador 1) (°C)': (230,210),
        'Rele desescarche (evaporador 1) (on/off)': (400,195),
        'Rele ventilador (evaporador 1) (on/off)': (215,440),
        'Rele valvula (evaporador 1) (on/off)': (395,275),
        'Presion de baja (valvula expansion 1) (bar)': (70,315),
        'Temperatura aspiracion (valvula expansion 1) (°C)': (70,280),
        'Recalentamiento (valvula expansion 1) (K)': (70,245),
        'Apertura valvula (valvula expansion 1) (%)': (410,245),
        'Potencia total (W)': (400,100),
        'Energia total (kWh)': (400,65),
        'Presion de baja (valvula expansion 2) (bar)':(1780,315),
        'Temperatura aspiracion (valvula expansion 2) (°C)': (1780,280),
        'Recalentamiento (valvula expansion 2) (K)': (1780,245),
        'Temperatura desescarche (evaporador 2) (°C)': (1650,210),
        'Rele desescarche (evaporador 2) (on/off)': (1420,195),
        'Rele ventilador (evaporador 2) (on/off)': (1605,440),
        'Apertura valvula (valvula expansion 2) (%)': (1450,245),
        'Rele valvula (evaporador 2) (on/off)': (1433,275)
        
        }

        # Definir las unidades para cada dato
        unidades = {
            "Temperatura evaporacion (°C)": "°C",  # Unidad para la temperatura de evaporación
            'Presion evaporacion (bar)': 'bar',
            'Presion condensacion (bar)': 'bar',
            'Temperatura condensacion (°C)': '°C',
            'Presion deposito (bar)': 'bar',
            'Temperatura deposito (°C)': '°C',
            'Temperatura exterior (°C)': '°C',
            'Temperatura salida gas cooler (°C)': '°C',
            'Temperatura aspiracion (°C)': '°C',
            'Temperatura descarga (°C)': '°C',
            'Temperatura liquido (°C)': '°C',
            'Potencia compresor (%)': '%',
            'Potencia ventilador gas-cooler (%)': '%',
            'Apertura valvula by-pass (%)': '%',
            'Apertura valvula alta presion (%)': '%',
            'Rele compresor (on/off)': 'on/off',
            'Temperatura camara (evaporador 1) (°C)': '°C',
            'Temperatura desescarche (evaporador 1) (°C)': '°C',
            'Rele desescarche (evaporador 1) (on/off)': 'on/off',
            'Rele ventilador (evaporador 1) (on/off)': 'on/off',
            'Rele valvula (evaporador 1) (on/off)': 'on/off',
            'Presion de baja (valvula expansion 1) (bar)': 'bar',
            'Temperatura aspiracion (valvula expansion 1) (°C)': '°C',
            'Recalentamiento (valvula expansion 1) (K)': 'K',
            'Apertura valvula (valvula expansion 1) (%)': '%',
            'Potencia total (W)': 'W',
            'Energia total (kWh)': 'kWh',
            'Presion de baja (valvula expansion 2) (bar)':('bar'),
            'Temperatura aspiracion (valvula expansion 2) (°C)': ('°C'),
            'Recalentamiento (valvula expansion 2) (K)': ('K'),
            'Temperatura desescarche (evaporador 2) (°C)': ('°C'),
            'Rele desescarche (evaporador 2) (on/off)': ('on/off'),
            'Rele ventilador (evaporador 2) (on/off)': ('on/off'),
            'Apertura valvula (valvula expansion 2) (%)': ('%'),
            'Rele valvula (evaporador 2) (on/off)': ('on/off')
        }

        # Crear un placeholder para la imagen en Streamlit
        imagen_placeholder = st.empty()

        # Crear una copia de la imagen original
        imagen_actualizada = imagen.copy()
        draw = ImageDraw.Draw(imagen_actualizada)
        # Superponer los datos en la imagen
        font = ImageFont.truetype("letras/Tinos-Regular.ttf", size=30)
        for dato, (x, y) in posiciones.items():
            if dato in df_ampliado_scada.columns and not pd.isna(df_ampliado_scada[dato].iloc[-1]):
                valor = str(df_ampliado_scada[dato].iloc[-1])  # Lee el valor del Excel
                unidad = unidades.get(dato, "")# Obtén la unidad correspondiente (o cadena vacía si no existe)
                texto = f"{valor} {unidad}"  # Concatena el valor y la unidad
            else:
                texto='--'
            draw.text((x, y), texto, fill="red", font=font)  # Dibuja el texto en la imagen
        # Mostrar la imagen actualizada en Streamlit
        imagen_placeholder.image(imagen_actualizada, caption="Instalación de CO2 transcrítica", use_container_width=True)

    # Preprocesar datos para gráficas
    if 'Gráfico de líneas' in tipo_grafico:
        df_ampliado_analogico = df_ampliado_analogico.reset_index().rename(columns={'index': 'Tiempo'})
        df_ampliado_analogico['Tiempo'] = df_ampliado_analogico['Tiempo'].dt.strftime("%H:%M")  # Formatear tiempo
        df_ampliado_analogico = df_ampliado_analogico.melt('Tiempo', var_name='Variable', value_name='Valor')
        df_ampliado_digital = df_ampliado_digital.reset_index().rename(columns={'index': 'Tiempo'})
        df_ampliado_digital['Tiempo'] = df_ampliado_digital['Tiempo'].dt.strftime("%H:%M")  # Formatear tiempo
        df_ampliado_digital = df_ampliado_digital.melt('Tiempo', var_name='Variable', value_name='Valor')

        #Creación de placeholders para las gráficas
        grafica_analogica = st.empty()  # Placeholder para la gráfica
        grafica_digital = st.empty() #Placeholder para la gráfica

        # Mostrar datos iniciales 
        figura_analogica = px.line(df_ampliado_analogico, x='Tiempo', y='Valor', color='Variable', title="Variables Analógicas")
        figura_analogica.update_layout(transition={'duration': 500})  # Efecto de transición
        figura_analogica.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))

        grafica_analogica.plotly_chart(figura_analogica)
        figura_digital = px.line(df_ampliado_digital, x='Tiempo', y='Valor', color='Variable', title="Variables Digitales")
        figura_digital.update_layout(transition={'duration': 500})  # Efecto de transición
        figura_digital.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',tickvals=[0, 1], range=[-0.1, 1.1],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
        grafica_digital.plotly_chart(figura_digital)
#

    while True:
#
        # Esperar un minuto antes de la próxima actualización
        sleep(60)

        #Token
        TOKEN = request_login(USERNAME, PASSWORD)
        
        # Obtener la fecha y hora actual
        ahora = datetime.now()
        ahora = ahora -timedelta(minutes=60)
        fecha_ahora = ahora.strftime("%H:%M_%Y%m%d")
        antes = ahora - timedelta(minutes=intervalo_visualizacion+1)
        fecha_antes=antes.strftime("%H:%M_%Y%m%d")
#
        #Intervalo de tiempo para llamar al servidor
        FROM_STR = fecha_antes
        UNTIL_STR = fecha_ahora
        INTERVAL = 60 # En segundos
#
        #Petición de histórico de datos al servidor y posterior procesamiento 
        response_analizador_redes = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_analizador_redes, ENTITIES_analizador_redes, FROM_STR, UNTIL_STR, INTERVAL)
        df_analizador_redes = process_charts_response(DEVICE_UUID, CONTROL_UUID_analizador_redes, ENTITIES_analizador_redes, response_analizador_redes)

        response_evaporador_04 = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_evaporador_04, ENTITIES_evaporador_04, FROM_STR, UNTIL_STR, INTERVAL)
        df_evaporador_04 = process_charts_response(DEVICE_UUID, CONTROL_UUID_evaporador_04, ENTITIES_evaporador_04, response_evaporador_04)
       
        response_valvula_expansion_05 = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_valvula_expansion_05, ENTITIES_valvula_expansion_05, FROM_STR, UNTIL_STR, INTERVAL)
        df_valvula_expansion_05 = process_charts_response(DEVICE_UUID, CONTROL_UUID_valvula_expansion_05, ENTITIES_valvula_expansion_05, response_valvula_expansion_05)

        response_evaporador_06 = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_evaporador_06, ENTITIES_evaporador_06, FROM_STR, UNTIL_STR, INTERVAL)
        df_evaporador_06 = process_charts_response(DEVICE_UUID, CONTROL_UUID_evaporador_06, ENTITIES_evaporador_06, response_evaporador_06)
      
        response_valvula_expansion_07 = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_valvula_expansion_07, ENTITIES_valvula_expansion_07, FROM_STR, UNTIL_STR, INTERVAL)
        df_valvula_expansion_07 = process_charts_response(DEVICE_UUID, CONTROL_UUID_valvula_expansion_07, ENTITIES_valvula_expansion_07, response_valvula_expansion_07)
     
        response_equipo = make_charts_request(TOKEN, DEVICE_UUID, CONTROL_UUID_equipo, ENTITIES_equipo, FROM_STR, UNTIL_STR, INTERVAL)
        df_equipo = process_charts_response(DEVICE_UUID, CONTROL_UUID_equipo, ENTITIES_equipo, response_equipo)
       
#
        #PREPROCESADO
#
        #Establecer el índice correcto
#
        df_analizador_redes.index = df_analizador_redes.index.tz_localize(None)
        df_analizador_redes.index=df_analizador_redes.index.floor('min')
        inicio_df_analizador_redes=df_analizador_redes.index[0]
        fin_df_analizador_redes=df_analizador_redes.index[-1]
        indice_nuevo_df_analizador_redes=pd.date_range(start=inicio_df_analizador_redes,end=fin_df_analizador_redes,freq='min')
        df_analizador_redes=df_analizador_redes.reindex(indice_nuevo_df_analizador_redes)
#
        df_evaporador_04.index = df_evaporador_04.index.tz_localize(None)
        df_evaporador_04.index=df_evaporador_04.index.floor('min')
        inicio_df_evaporador_04=df_evaporador_04.index[0]
        fin_df_evaporador_04=df_evaporador_04.index[-1]
        indice_nuevo_df_evaporador_04=pd.date_range(start=inicio_df_evaporador_04,end=fin_df_evaporador_04,freq='min')
        df_evaporador_04=df_evaporador_04.reindex(indice_nuevo_df_evaporador_04)
#
        df_valvula_expansion_05.index = df_valvula_expansion_05.index.tz_localize(None)
        df_valvula_expansion_05.index=df_valvula_expansion_05.index.floor('min')
        inicio_df_valvula_expansion_05=df_valvula_expansion_05.index[0]
        fin_df_valvula_expansion_05=df_valvula_expansion_05.index[-1]
        indice_nuevo_df_valvula_expansion_05=pd.date_range(start=inicio_df_valvula_expansion_05,end=fin_df_valvula_expansion_05,freq='min')
        df_valvula_expansion_05=df_valvula_expansion_05.reindex(indice_nuevo_df_valvula_expansion_05)
#
        df_evaporador_06.index = df_evaporador_06.index.tz_localize(None)
        df_evaporador_06.index=df_evaporador_06.index.floor('min')
        inicio_df_evaporador_06=df_evaporador_06.index[0]
        fin_df_evaporador_06=df_evaporador_06.index[-1]
        indice_nuevo_df_evaporador_06=pd.date_range(start=inicio_df_evaporador_06,end=fin_df_evaporador_06,freq='min')
        df_evaporador_06=df_evaporador_06.reindex(indice_nuevo_df_evaporador_06)
#
        df_valvula_expansion_07.index = df_valvula_expansion_07.index.tz_localize(None)
        df_valvula_expansion_07.index=df_valvula_expansion_07.index.floor('min')
        inicio_df_valvula_expansion_07=df_valvula_expansion_07.index[0]
        fin_df_valvula_expansion_07=df_valvula_expansion_07.index[-1]
        indice_nuevo_df_valvula_expansion_07=pd.date_range(start=inicio_df_valvula_expansion_07,end=fin_df_valvula_expansion_07,freq='min')
        df_valvula_expansion_07=df_valvula_expansion_07.reindex(indice_nuevo_df_valvula_expansion_07)
#
        df_equipo.index = df_equipo.index.tz_localize(None)
        df_equipo.index=df_equipo.index.floor('min')
        inicio_df_equipo=df_equipo.index[0]
        fin_df_equipo=df_equipo.index[-1]
        indice_nuevo_df_equipo=pd.date_range(start=inicio_df_equipo,end=fin_df_equipo,freq='min')
        df_equipo=df_equipo.reindex(indice_nuevo_df_equipo)
#
        #Rellenado de datos omitidos
#
        columnas_no_vacias = df_analizador_redes.columns[~df_analizador_redes.isna().all()].tolist()
        df_analizador_redes[columnas_no_vacias]=df_analizador_redes[columnas_no_vacias].interpolate()
        df_analizador_redes[columnas_no_vacias]=df_analizador_redes[columnas_no_vacias].bfill()
        df_analizador_redes[columnas_no_vacias]=df_analizador_redes[columnas_no_vacias].ffill()
        df_analizador_redes[columnas_no_vacias]=df_analizador_redes[columnas_no_vacias].round(2)
#
        columnas_no_vacias = df_evaporador_04.columns[~df_evaporador_04.isna().all()].tolist()
        df_evaporador_04[columnas_no_vacias]=df_evaporador_04[columnas_no_vacias].interpolate()
        df_evaporador_04[columnas_no_vacias]=df_evaporador_04[columnas_no_vacias].bfill()
        df_evaporador_04[columnas_no_vacias]=df_evaporador_04[columnas_no_vacias].ffill()
        df_evaporador_04[columnas_no_vacias]=df_evaporador_04[columnas_no_vacias].round(2)
#
        columnas_no_vacias = df_valvula_expansion_05.columns[~df_valvula_expansion_05.isna().all()].tolist()
        df_valvula_expansion_05[columnas_no_vacias]=df_valvula_expansion_05[columnas_no_vacias].interpolate()
        df_valvula_expansion_05[columnas_no_vacias]=df_valvula_expansion_05[columnas_no_vacias].bfill()
        df_valvula_expansion_05[columnas_no_vacias]=df_valvula_expansion_05[columnas_no_vacias].ffill()
        df_valvula_expansion_05[columnas_no_vacias]=df_valvula_expansion_05[columnas_no_vacias].round(2)
#
        columnas_no_vacias = df_evaporador_06.columns[~df_evaporador_06.isna().all()].tolist()
        df_evaporador_06[columnas_no_vacias]=df_evaporador_06[columnas_no_vacias].interpolate()
        df_evaporador_06[columnas_no_vacias]=df_evaporador_06[columnas_no_vacias].bfill()
        df_evaporador_06[columnas_no_vacias]=df_evaporador_06[columnas_no_vacias].ffill()
        df_evaporador_06[columnas_no_vacias]=df_evaporador_06[columnas_no_vacias].round(2)
#
        columnas_no_vacias = df_valvula_expansion_07.columns[~df_valvula_expansion_07.isna().all()].tolist()
        df_valvula_expansion_07[columnas_no_vacias]=df_valvula_expansion_07[columnas_no_vacias].interpolate()
        df_valvula_expansion_07[columnas_no_vacias]=df_valvula_expansion_07[columnas_no_vacias].bfill()
        df_valvula_expansion_07[columnas_no_vacias]=df_valvula_expansion_07[columnas_no_vacias].ffill()
        df_valvula_expansion_07[columnas_no_vacias]=df_valvula_expansion_07[columnas_no_vacias].round(2)
#
        columnas_no_vacias = df_equipo.columns[~df_equipo.isna().all()].tolist()
        df_equipo[columnas_no_vacias]=df_equipo[columnas_no_vacias].interpolate()
        df_equipo[columnas_no_vacias]=df_equipo[columnas_no_vacias].bfill()
        df_equipo[columnas_no_vacias]=df_equipo[columnas_no_vacias].ffill()
        df_equipo[columnas_no_vacias]=df_equipo[columnas_no_vacias].round(2)
#
        #Concatenar los dataframe que tienen columnas seleccionadas
        df_ampliado=pd.concat([df_analizador_redes,df_equipo,df_evaporador_04,df_valvula_expansion_05,df_evaporador_06,df_valvula_expansion_07],axis=1)
        df_ampliado=df_ampliado[lista_variables]
        variables_analogicas=["Potencia total (W)","Energia total (kWh)","Temperatura camara (evaporador 1) (°C)","Temperatura desescarche (evaporador 1) (°C)","Presion de baja (valvula expansion 1) (bar)","Temperatura aspiracion (valvula expansion 1) (°C)","Recalentamiento (valvula expansion 1) (K)","Apertura valvula (valvula expansion 1) (%)","Temperatura camara (evaporador 2) (°C)","Temperatura desescarche (evaporador 2) (°C)","Presion de baja (valvula expansion 2) (bar)","Temperatura aspiracion (valvula expansion 2) (°C)","Recalentamiento (valvula expansion 2) (K)","Apertura valvula (valvula expansion 2) (%)",'Presion evaporacion (bar)','Temperatura evaporacion (°C)',"Presion condensacion (bar)","Temperatura condensacion (°C)","Presion deposito (bar)","Temperatura deposito (°C)","Temperatura exterior (°C)","Temperatura salida gas cooler (°C)","Temperatura aspiracion (°C)","Temperatura descarga (°C)","Temperatura liquido (°C)","Potencia compresor (%)","Potencia ventilador gas-cooler (%)","Apertura valvula by-pass (%)","Apertura valvula alta presion (%)"]
        variables_digitales=["Rele desescarche (evaporador 1) (on/off)","Rele ventilador (evaporador 1) (on/off)","Rele valvula (evaporador 1) (on/off)","Estado desescarche (evaporador 1) (on/off)","Estado dispositivo (evaporador 1) (on/off)","Estado valvula (valvula expansion 1) (on/off)","Rele desescarche (evaporador 2) (on/off)","Rele ventilador (evaporador 2) (on/off)","Rele valvula (evaporador 2) (on/off)","Estado desescarche (evaporador 2) (on/off)","Estado dispositivo (evaporador 2) (on/off)","Estado valvula (valvula expansion 2) (on/off)","Rele compresor (on/off)"]
        lista_variables_analogicas=list(set(variables_analogicas) & set(lista_variables))
        lista_variables_digitales=list(set(variables_digitales) & set(lista_variables))
        df_ampliado_analogico=df_ampliado[lista_variables_analogicas]
        df_ampliado_digital=df_ampliado[lista_variables_digitales]
        df_ampliado_scada=pd.concat([df_ampliado_analogico,df_ampliado_digital],axis=1)
        df_ampliado_tabla=df_ampliado_scada
        df_ampliado_tabla.index = df_ampliado_tabla.index.strftime('%H:%M')

        if 'Tabla' in tipo_grafico:
##
            # Inicializar un DataFrame vacío para la tabla
            tabla_datos = pd.DataFrame(columns=lista_variables)
            tabla_datos.index.name = 'Hora'
##
            tabla_datos = df_ampliado_scada.copy()
            tabla_datos.index = df_ampliado_tabla.index
##
            # Mostrar la tabla actualizada
            tabla_placeholder.dataframe(tabla_datos,use_container_width=True)

        if 'Scada' in tipo_grafico:
        # Crear una copia de la imagen original
            imagen_actualizada = imagen.copy()
            draw = ImageDraw.Draw(imagen_actualizada)
            # Superponer los datos en la imagen
            font = ImageFont.truetype("letras/Tinos-Regular.ttf", size=30)
            for dato, (x, y) in posiciones.items():
                if dato in df_ampliado_scada.columns and not pd.isna(df_ampliado_scada[dato].iloc[-1]):
                    valor = str(df_ampliado_scada[dato].iloc[-1])  # Lee el valor del Excel
                    unidad = unidades.get(dato, "")# Obtén la unidad correspondiente (o cadena vacía si no existe)
                    texto = f"{valor} {unidad}"  # Concatena el valor y la unidad
                else:
                    texto='--'
                draw.text((x, y), texto, fill="red", font=font)  # Dibuja el texto en la imagen
            # Mostrar la imagen actualizada en Streamlit
            imagen_placeholder.image(imagen_actualizada, caption="Instalación de CO2 transcrítica", use_container_width=True)

 #
         # Preprocesar datos para gráficas
        if 'Gráfico de líneas' in tipo_grafico:
            df_ampliado_analogico = df_ampliado_analogico.reset_index().rename(columns={'index': 'Tiempo'})
            df_ampliado_analogico['Tiempo'] = df_ampliado_analogico['Tiempo'].dt.strftime("%H:%M")  # Formatear tiempo
            df_ampliado_analogico = df_ampliado_analogico.melt('Tiempo', var_name='Variable', value_name='Valor')
            df_ampliado_digital = df_ampliado_digital.reset_index().rename(columns={'index': 'Tiempo'})
            df_ampliado_digital['Tiempo'] = df_ampliado_digital['Tiempo'].dt.strftime("%H:%M")  # Formatear tiempo
            df_ampliado_digital = df_ampliado_digital.melt('Tiempo', var_name='Variable', value_name='Valor')

            figura_analogica = px.line(df_ampliado_analogico, x='Tiempo', y='Valor', color='Variable', title="Variables Analógicas")
            figura_analogica.update_layout(transition={'duration': 500})  # Efecto de transición
            figura_analogica.update_layout(
                        width=None,
                        height=500,
                        legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                        xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                        yaxis=dict(showgrid=True,gridcolor='lightgray',mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
            grafica_analogica.plotly_chart(figura_analogica)
            figura_digital = px.line(df_ampliado_digital, x='Tiempo', y='Valor', color='Variable', title="Variables Digitales")
            figura_digital.update_layout(transition={'duration': 500})  # Efecto de transición
            figura_digital.update_layout(
                        width=None,
                        height=500,
                        legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                        xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                        yaxis=dict(showgrid=True,gridcolor='lightgray',tickvals=[0, 1], range=[-0.1, 1.1],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
            grafica_digital.plotly_chart(figura_digital)