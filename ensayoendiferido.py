from datetime import datetime         
import pandas as pd
import matplotlib.pyplot as plt     
import numpy as np
import streamlit as st
import altair as alt
from time import sleep
import plotly.express as px
from PIL import Image, ImageDraw, ImageFont
import CoolProp.CoolProp as CP
from scipy.optimize import minimize_scalar
from scipy.optimize import minimize
import plotly.graph_objects as go
from plotly.subplots import make_subplots





#Definición de función
def representacion_grafico(indicadores_termodinamicos,velocidad_reproduccion,tipo_grafico_diferido,lista_variables_diferido,df_analizador_redes_ensayo,df_equipo_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo):
    lista_indicadores=['COP','Diagramas P-H y T-S','Potencias del ciclo','Flujos másicos','Rendimientos del compresor','Caracterización de los evaporadores']
    set_indicadores_termodinamicos=set(indicadores_termodinamicos)
    set_lista_indicadores=set(lista_indicadores)
    #Indicadores termodinámicos
    if set_indicadores_termodinamicos & set_lista_indicadores:
        media=pd.concat([df_equipo_ensayo,df_analizador_redes_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo],axis=1)
        media["Tiempo"] = range(len(media))
        media["Indice"] = media.index.strftime('%H:%M')
        media=media.reset_index(drop=True) #Convierte índice

    #Concatenar los dataframe que tienen columnas seleccionadas
    df_ampliado=pd.concat([df_equipo_ensayo,df_analizador_redes_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo],axis=1)
    df_ampliado=df_ampliado[lista_variables_diferido]
    variables_analogicas=["Potencia total (W)","Energia total (kWh)","Temperatura camara (evaporador 1) (°C)","Temperatura desescarche (evaporador 1) (°C)","Presion de baja (valvula expansion 1) (bar)","Temperatura aspiracion (valvula expansion 1) (°C)","Recalentamiento (valvula expansion 1) (K)","Apertura valvula (valvula expansion 1) (%)","Temperatura camara (evaporador 2) (°C)","Temperatura desescarche (evaporador 2) (°C)","Presion de baja (valvula expansion 2) (bar)","Temperatura aspiracion (valvula expansion 2) (°C)","Recalentamiento (valvula expansion 2) (K)","Apertura valvula (valvula expansion 2) (%)",'Presion evaporacion (bar)','Temperatura evaporacion (°C)',"Presion condensacion (bar)","Temperatura condensacion (°C)","Presion deposito (bar)","Temperatura deposito (°C)","Temperatura exterior (°C)","Temperatura salida gas cooler (°C)","Temperatura aspiracion (°C)","Temperatura descarga (°C)","Temperatura liquido (°C)","Potencia compresor (%)","Potencia ventilador gas-cooler (%)","Apertura valvula by-pass (%)","Apertura valvula alta presion (%)"]
    variables_digitales=["Rele desescarche (evaporador 1) (on/off)","Rele ventilador (evaporador 1) (on/off)","Rele valvula (evaporador 1) (on/off)","Estado desescarche (evaporador 1) (on/off)","Estado dispositivo (evaporador 1) (on/off)","Estado valvula (valvula expansion 1) (on/off)","Rele desescarche (evaporador 2) (on/off)","Rele ventilador (evaporador 2) (on/off)","Rele valvula (evaporador 2) (on/off)","Estado desescarche (evaporador 2) (on/off)","Estado dispositivo (evaporador 2) (on/off)","Estado valvula (valvula expansion 2) (on/off)","Rele compresor (on/off)"]
    lista_variables_analogicas=list(set(variables_analogicas) & set(lista_variables_diferido))
    lista_variables_digitales=list(set(variables_digitales) & set(lista_variables_diferido))
    df_ampliado_analogico=df_ampliado[lista_variables_analogicas]
    df_ampliado_digital=df_ampliado[lista_variables_digitales]
    df_ampliado_scada=pd.concat([df_ampliado_analogico,df_ampliado_digital],axis=1)
    df_ampliado_tabla=df_ampliado_scada
    df_ampliado_tabla["Indice"] = df_ampliado.index.strftime('%H:%M')

    df_ampliado_analogico["Tiempo"] = range(len(df_ampliado_analogico))
    df_ampliado_analogico["Indice"] = df_ampliado_analogico.index.strftime('%H:%M')
    df_ampliado_digital["Tiempo"] = range(len(df_ampliado_digital))
    df_ampliado_digital["Indice"] = df_ampliado_digital.index.strftime('%H:%M')

    #Placeholder para el indicador del tiempo
    tiempo=st.empty()
    # Crear una placeholder para la gráfica
    if 'Gráfico de líneas' in tipo_grafico_diferido and lista_variables_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        chart_analogica = st.empty()  # Placeholder para la gráfica
        chart_digital = st.empty() #Placeholder para la gráfica

    if 'Tabla' in tipo_grafico_diferido and lista_variables_diferido:
        st.markdown("<br>", unsafe_allow_html=True) 
        #Información
        st.markdown("<p style='font-size: 17px;'><strong>Tabla dinámica</strong></p>", unsafe_allow_html=True)

        tabla_placeholder = st.empty()  # Placeholder para la tabla
    # Inicializar un DataFrame vacío para la tabla
        tabla_datos = pd.DataFrame(columns=lista_variables_diferido)
        tabla_datos.index.name = 'Hora'

    if 'Scada' in tipo_grafico_diferido and lista_variables_diferido:
        st.markdown("<br>", unsafe_allow_html=True) 
        #Información
        st.markdown("<p style='font-size: 17px;'><strong>Scada dinámico</strong></p>", unsafe_allow_html=True)
 
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
            'Temperatura camara (evaporador 1) (°C) ': '°C',
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

    if 'Diagramas P-H y T-S' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:
        # Placeholder para indicadores termodinámicos
        st.markdown("<br>", unsafe_allow_html=True)
        diagrama = make_subplots(rows=1, cols=2, subplot_titles=("<b>P-H</b>", "<b>T-S</b>"))
        diagrama.update_annotations(font=dict(color='black', size=16))

        diagrama_placeholder = st.empty()

    if 'Diagramas P-H y T-S' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 17px;'><strong>Tabla propiedades termodinámicas</strong></p>", unsafe_allow_html=True)
        tabla_placeholder_propiedades = st.empty()  # Placeholder para la tabla


    if 'COP' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        grafica_cop=st.empty()

    if 'Potencias del ciclo' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        grafica_potencias=st.empty()

    if 'COP' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 17px;'><strong>Tabla de coeficientes de rendimiento</strong></p>", unsafe_allow_html=True)
        tabla_placeholder_cop = st.empty()  # Placeholder para la tabla
        # Inicializar un DataFrame vacío para la tabla
        tabla_datos_cop = pd.DataFrame(columns=['COP (EER)','COP (BC)'])
        tabla_datos_cop.index.name = 'Hora'

    if 'Potencias del ciclo' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 17px;'><strong>Tabla de potencias</strong></p>", unsafe_allow_html=True)
        tabla_placeholder_potencias = st.empty()  # Placeholder para la tabla
        # Inicializar un DataFrame vacío para la tabla
        tabla_datos_potencias = pd.DataFrame(columns=['Potencia frigorífica (evaporadores) (kW)','Potencia cedida (gas-cooler) (kW)','Potencia ideal (compresor) (kW)','Consumo eléctrico (compresor) (kW)'])
        tabla_datos_potencias.index.name = 'Hora'  

    if 'Flujos másicos' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        grafica_flujos=st.empty()


    if 'Flujos másicos' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 17px;'><strong>Tabla de flujos másicos</strong></p>", unsafe_allow_html=True)
        tabla_placeholder_flujos = st.empty()  # Placeholder para la tabla
        # Inicializar un DataFrame vacío para la tabla
        tabla_datos_flujos = pd.DataFrame(columns=['Flujo másico (refrigerante bifásico) (Kg/s)','Flujo másico (refrigerante vapor saturado) (Kg/s)','Flujo másico (refrigerante líquido saturado) (Kg/s)'])
        tabla_datos_flujos.index.name = 'Hora'  

    if 'Rendimientos del compresor' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        grafica_rendimientos=st.empty()

    if 'Rendimientos del compresor' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 17px;'><strong>Tabla de rendimientos</strong></p>", unsafe_allow_html=True)
        tabla_placeholder_rendimientos = st.empty()  # Placeholder para la tabla
        # Inicializar un DataFrame vacío para la tabla
        tabla_datos_rendimientos = pd.DataFrame(columns=['Rendimiento volumétrico (primera etapa de compresión) (%)','Rendimiento volumétrico (segunda estapa de compresión) (%)','Rendimiento isentrópico (primera y segunda etapa de compresión) (%)'])
        tabla_datos_rendimientos.index.name = 'Hora'  

    if 'Caracterización de los evaporadores' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        grafica_efectividad=st.empty()
        grafica_saltos=st.empty()

    if 'Caracterización de los evaporadores' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 17px;'><strong>Tabla de efectividad y saltos térmicos</strong></p>", unsafe_allow_html=True)
        tabla_placeholder_evaporadores = st.empty()  # Placeholder para la tabla
        # Inicializar un DataFrame vacío para la tabla
        tabla_datos_evaporadores = pd.DataFrame(columns=['Efectividad (evaporador 1) (%)','Efectividad (evaporador 2) (%)','Salto térmico (entrada - evaporador 1) (K)','Salto térmico (salida - evaporador 1) (K)','Salto térmico (entrada - evaporador 2) (K)','Salto térmico (salida - evaporador 2) (K)'])
        tabla_datos_evaporadores.index.name = 'Hora' 



    lista_tiempo=df_ampliado_analogico["Indice"].tolist()
    for i in range(len(df_ampliado_analogico)):
        tiempo.write(f'Minuto: {i} - Hora: {lista_tiempo[i]}')


        if 'Gráfico de líneas' in tipo_grafico_diferido and lista_variables_diferido:
            # Gráfica analógica
            if not df_ampliado_analogico.empty and any(col in df_ampliado_analogico.columns for col in lista_variables_diferido):
                df_actual_analogico = df_ampliado_analogico.iloc[:i + 1]
                df_melted_analogico = df_actual_analogico.melt(id_vars=['Tiempo','Indice'], var_name='Variable', value_name='Valor')

                fig_analogica = px.line(
                    df_melted_analogico,
                    x='Tiempo',
                    y='Valor',
                    color='Variable',
                    labels={'Tiempo': 'Tiempo (minutos)', 'Valor': 'Valor'},
                    title='Gráfica dinámica de variables analógicas',custom_data=['Indice'])
                fig_analogica.update_traces(
                    hovertemplate="Tiempo: %{x}<br>Valor: %{y}<br>Hora: %{customdata[0]}<br>Variable: %{fullData.name}<extra></extra>"
                )
                fig_analogica.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
                chart_analogica.plotly_chart(fig_analogica)

                # Gráfica digital
            if not df_ampliado_digital.empty and any(col in df_ampliado_digital.columns for col in lista_variables_diferido):
                df_actual_digital = df_ampliado_digital.iloc[:i + 1]
                df_melted_digital = df_actual_digital.melt(id_vars=['Tiempo','Indice'], var_name='Variable', value_name='Valor')

                fig_digital = px.line(
                    df_melted_digital,
                    x='Tiempo',
                    y='Valor',
                    color='Variable',
                    labels={'Tiempo': 'Tiempo (minutos)', 'Valor': 'Estado'},
                    title='Gráfica dinámica de variables digitales',custom_data=['Indice'])
                fig_digital.update_traces(
                    hovertemplate="Tiempo: %{x}<br>Valor: %{y}<br>Hora: %{customdata[0]}<br>Variable: %{fullData.name}<extra></extra>"
                )
                # Ajustes específicos para señales digitales
                fig_digital.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',tickvals=[0, 1], range=[-0.1, 1.1],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
                chart_digital.plotly_chart(fig_digital)

  

        if 'Tabla' in tipo_grafico_diferido and lista_variables_diferido:

             # Actualizar la tabla con los datos actuales
            hora_actual = df_ampliado_tabla.iloc[i]["Indice"]
            fila_actual = df_ampliado.iloc[i].to_frame().T
            fila_actual.index = [hora_actual]
            tabla_datos = pd.concat([tabla_datos, fila_actual])
            # Mostrar la tabla actualizada
            tabla_placeholder.dataframe(tabla_datos,use_container_width=True)



        if 'Scada' in tipo_grafico_diferido and lista_variables_diferido:

            # Crear una copia de la imagen original
            imagen_actualizada = imagen.copy()
            draw = ImageDraw.Draw(imagen_actualizada)

            # Superponer los datos en la imagen
            font = ImageFont.truetype("letras/Tinos-Regular.ttf", size=30)
            for dato, (x, y) in posiciones.items():
                if dato in df_ampliado_scada.columns and not pd.isna(df_ampliado_scada[dato].iloc[i]):
                    valor = str(df_ampliado_scada[dato].iloc[i])  # Lee el valor del Excel
                    unidad = unidades.get(dato, "")# Obtén la unidad correspondiente (o cadena vacía si no existe)
                    texto = f"{valor} {unidad}"  # Concatena el valor y la unidad
                else:
                    texto='--'
                draw.text((x, y), texto, fill="red", font=font)  # Dibuja el texto en la imagen

            # Mostrar la imagen actualizada en Streamlit
            imagen_placeholder.image(imagen_actualizada, caption="Instalación de CO2 transcrítica", use_container_width=True)


        if set_indicadores_termodinamicos & set_lista_indicadores:
  
            tabla_propiedades=pd.DataFrame(columns=['Temperatura (°C)','Presión (bar)','Entalpía (kJ/Kg)','Entropía (kJ/Kg·K)','Título de vapor','Densidad (Kg/m^3)','Caudal másico (Kg/s)'],index=['1','2','3','4s','4','5','6s','6','7','8','9','10','11','12','13','14'])

            #Punto 1
            if ('Presion de baja (valvula expansion 1) (bar)' in media.columns) and ('Presion de baja (valvula expansion 2) (bar)' in media.columns):
                presion_evaporacion=(media.loc[i,'Presion evaporacion (bar)']+media.loc[i,'Presion de baja (valvula expansion 1) (bar)']+media.loc[i,'Presion de baja (valvula expansion 2) (bar)'])/3
            else:
                presion_evaporacion=media.loc[i,'Presion evaporacion (bar)']
            tabla_propiedades.loc['1','Temperatura (°C)']=(CP.PropsSI("T", "P", presion_evaporacion*(10**5), "Q",1 , "CO2"))-273.15 #Temperatura de evaporación
            tabla_propiedades.loc['1','Presión (bar)']=presion_evaporacion
            tabla_propiedades.loc['1','Título de vapor']=1.000
            tabla_propiedades.loc['1','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P", presion_evaporacion*(10**5), "Q",1 , "CO2"))/1000
            tabla_propiedades.loc['1','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",presion_evaporacion*(10**5) , "Q", 1, "CO2"))/1000
            tabla_propiedades.loc['1','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",presion_evaporacion*(10**5) , "Q", 1, "CO2")

            #Punto 2
            if ('Recalentamiento (valvula expansion 1) (K)' in media.columns) and ('Recalentamiento (valvula expansion 2) (K)' in media.columns):
                tabla_propiedades.loc['2','Temperatura (°C)']=(CP.PropsSI("T", "P", presion_evaporacion*(10**5), "Q",1 , "CO2"))-273.15+abs((media.loc[i,'Recalentamiento (valvula expansion 1) (K)']+media.loc[i,'Recalentamiento (valvula expansion 2) (K)'])/2)
                tabla_propiedades.loc['2','Temperatura (°C)']=(tabla_propiedades.loc['2','Temperatura (°C)']+media.loc[i,'Temperatura aspiracion (°C)'])/2 
                temperatura_sobrecalentado=tabla_propiedades.loc['2','Temperatura (°C)']
            elif ('Temperatura aspiracion (valvula expansion 1) (°C)' in media.columns) and ('Temperatura aspiracion (valvula expansion 2) (°C)' in media.columns):
                tabla_propiedades.loc['2','Temperatura (°C)']=(media.loc[i,'Temperatura aspiracion (valvula expansion 1) (°C)']+media.loc[i,'Temperatura aspiracion (valvula expansion 2) (°C)']+media.loc[i,'Temperatura aspiracion (°C)'])/3 
                temperatura_sobrecalentado=tabla_propiedades.loc['2','Temperatura (°C)']
            else:
                tabla_propiedades.loc['2','Temperatura (°C)']=media.loc[i,'Temperatura aspiracion (°C)']
                temperatura_sobrecalentado=tabla_propiedades.loc['2','Temperatura (°C)']
            tabla_propiedades.loc['2','Presión (bar)']=presion_evaporacion
            tabla_propiedades.loc['2','Título de vapor']=None
            tabla_propiedades.loc['2','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P", presion_evaporacion*(10**5), "T",temperatura_sobrecalentado+273.15 , "CO2"))/1000
            tabla_propiedades.loc['2','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",presion_evaporacion*(10**5) , "T", temperatura_sobrecalentado+273.15, "CO2"))/1000
            tabla_propiedades.loc['2','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",presion_evaporacion*(10**5) , "T", temperatura_sobrecalentado+273.15, "CO2")

            #Punto 6
            tabla_propiedades.loc['6','Temperatura (°C)']=media.loc[i,'Temperatura descarga (°C)']
            tabla_propiedades.loc['6','Presión (bar)']=media.loc[i,'Presion condensacion (bar)']
            tabla_propiedades.loc['6','Título de vapor']=None
            tabla_propiedades.loc['6','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P", media.loc[i,'Presion condensacion (bar)']*(10**5), "T",media.loc[i,'Temperatura descarga (°C)']+273.15 , "CO2"))/1000
            tabla_propiedades.loc['6','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "T", media.loc[i,'Temperatura descarga (°C)']+273.15, "CO2"))/1000
            tabla_propiedades.loc['6','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "T", media.loc[i,'Temperatura descarga (°C)']+273.15, "CO2")    

            #Punto 7
            tabla_propiedades.loc['7','Temperatura (°C)']=media.loc[i,'Temperatura salida gas cooler (°C)']
            tabla_propiedades.loc['7','Presión (bar)']=media.loc[i,'Presion condensacion (bar)'] 
            tabla_propiedades.loc['7','Título de vapor']=None
            tabla_propiedades.loc['7','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P", media.loc[i,'Presion condensacion (bar)']*(10**5), "T",media.loc[i,'Temperatura salida gas cooler (°C)']+273.15 , "CO2"))/1000
            tabla_propiedades.loc['7','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "T", media.loc[i,'Temperatura salida gas cooler (°C)']+273.15, "CO2"))/1000
            tabla_propiedades.loc['7','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "T", media.loc[i,'Temperatura salida gas cooler (°C)']+273.15, "CO2")           

            #Punto 8
            tabla_propiedades.loc['8','Presión (bar)']=media.loc[i,'Presion deposito (bar)'] 
            tabla_propiedades.loc['8','Entalpía (kJ/Kg)']=tabla_propiedades.loc['7','Entalpía (kJ/Kg)']
            tabla_propiedades.loc['8','Título de vapor']=CP.PropsSI("Q", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2")
            tabla_propiedades.loc['8','Temperatura (°C)']=(CP.PropsSI("T", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2"))-273.15
            tabla_propiedades.loc['8','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2")
            tabla_propiedades.loc['8','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['7','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
            tabla_propiedades.loc['8','Título de vapor']=round(tabla_propiedades.loc['8','Título de vapor'],3)

            #Punto 9
            tabla_propiedades.loc['9','Presión (bar)']=media.loc[i,'Presion deposito (bar)'] 
            tabla_propiedades.loc['9','Título de vapor']=0.000
            tabla_propiedades.loc['9','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "Q",0, "CO2"))/1000
            tabla_propiedades.loc['9','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "Q",0, "CO2"))/1000
            tabla_propiedades.loc['9','Temperatura (°C)']=(CP.PropsSI("T", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "Q",0, "CO2"))-273.15
            tabla_propiedades.loc['9','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "Q", 0, "CO2")

            #Punto 10
            tabla_propiedades.loc['10','Entalpía (kJ/Kg)']=tabla_propiedades.loc['9','Entalpía (kJ/Kg)']
            tabla_propiedades.loc['10','Presión (bar)']=presion_evaporacion
            tabla_propiedades.loc['10','Título de vapor']=CP.PropsSI("Q", "P",presion_evaporacion*(10**5) , "H", tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2")
            tabla_propiedades.loc['10','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",presion_evaporacion*(10**5) , "H",tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
            tabla_propiedades.loc['10','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",presion_evaporacion*(10**5) , "H",tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
            tabla_propiedades.loc['10','Temperatura (°C)']=tabla_propiedades.loc['1','Temperatura (°C)']
            tabla_propiedades.loc['10','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",presion_evaporacion*(10**5) , "H", tabla_propiedades.loc['10','Entalpía (kJ/Kg)']*1000, "CO2")
            tabla_propiedades.loc['10','Título de vapor']=round(tabla_propiedades.loc['10','Título de vapor'],3)

            #Punto 11
            tabla_propiedades.loc['11','Presión (bar)']=media.loc[i,'Presion deposito (bar)'] 
            tabla_propiedades.loc['11','Título de vapor']=1.000
            tabla_propiedades.loc['11','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "Q",1, "CO2"))/1000
            tabla_propiedades.loc['11','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "Q",1, "CO2"))/1000
            tabla_propiedades.loc['11','Temperatura (°C)']=(CP.PropsSI("T", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "Q",1, "CO2"))-273.15
            tabla_propiedades.loc['11','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "Q", 1, "CO2")

            #Punto 12
            tabla_propiedades.loc['12','Presión (bar)']=tabla_propiedades.loc['11','Presión (bar)']
            tabla_propiedades.loc['12','Entalpía (kJ/Kg)']=tabla_propiedades.loc['11','Entalpía (kJ/Kg)']
            tabla_propiedades.loc['12','Temperatura (°C)']=tabla_propiedades.loc['11','Temperatura (°C)']
            tabla_propiedades.loc['12','Título de vapor']=tabla_propiedades.loc['11','Título de vapor']
            tabla_propiedades.loc['12','Entalpía (kJ/Kg)']=tabla_propiedades.loc['11','Entalpía (kJ/Kg)']
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

            if media.loc[i,'Potencia compresor (%)']>50:
               F=1.6*media.loc[i,'Potencia compresor (%)']/2
            else:
               F=80/2

            R_volumetrico_baja_teorico=16.6771332-0.01201859*media.loc[i,'Presion condensacion (bar)']-0.24571796*presion_evaporacion+3.20332109*F-0.00191565*media.loc[i,'Presion condensacion (bar)']**2-0.00219801*(presion_evaporacion**2)-0.02935512*(F**2)+0.00394487*media.loc[i,'Presion condensacion (bar)']*presion_evaporacion-0.00015889*media.loc[i,'Presion condensacion (bar)']*F+0.00468126*presion_evaporacion*F
            R_volumetrico_alta_teorico=(16.6771332-0.01201859*media.loc[i,'Presion condensacion (bar)']-0.24571796*presion_evaporacion+3.20332109*F-0.00191565*media.loc[i,'Presion condensacion (bar)']**2-0.00219801*(presion_evaporacion**2)-0.02935512*(F**2)+0.00394487*media.loc[i,'Presion condensacion (bar)']*presion_evaporacion-0.00015889*media.loc[i,'Presion condensacion (bar)']*F+0.00468126*presion_evaporacion*F)*(5.6/8)
            R_isentropico=20.4779885-0.08736845*tabla_propiedades.loc['6','Presión (bar)']+1.02075047*presion_evaporacion+1.6838928*F-0.00394391*(tabla_propiedades.loc['6','Presión (bar)']**2)-0.03363405*(presion_evaporacion**2)-0.01626644*(F**2)+0.01909573*tabla_propiedades.loc['6','Presión (bar)']*presion_evaporacion+0.00315153*tabla_propiedades.loc['6','Presión (bar)']*F-0.01128725*presion_evaporacion*F 
    
            if media.loc[i,'Apertura valvula by-pass (%)']==0:
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

                    tabla_propiedades.loc['5','Presión (bar)']=media.loc[i,'Presion deposito (bar)']
                    tabla_propiedades.loc['5','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))-273.15
                    tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000
                    tabla_propiedades.loc['5','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D",tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000

                    tabla_propiedades.loc['4s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']
                    tabla_propiedades.loc['4s','Presión (bar)']=media.loc[i,'Presion deposito (bar)']
                    tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "S",tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
                    tabla_propiedades.loc['4s','Temperatura (°C)']=(CP.PropsSI("T", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
                    tabla_propiedades.loc['4s','Caudal másico (Kg/s)']=0
                    tabla_propiedades.loc['4s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2")

                    tabla_propiedades.loc['6s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']
                    tabla_propiedades.loc['6s','Presión (bar)']=media.loc[i,'Presion condensacion (bar)']
                    tabla_propiedades.loc['6s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "S",tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
                    tabla_propiedades.loc['6s','Temperatura (°C)']=(CP.PropsSI("T", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
                    tabla_propiedades.loc['6s','Caudal másico (Kg/s)']=0
                    tabla_propiedades.loc['6s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2")

                    tabla_propiedades.loc['4','Entalpía (kJ/Kg)']=tabla_propiedades.loc['3','Entalpía (kJ/Kg)']+(tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])/(R_isentropico/100)
                    tabla_propiedades.loc['4','Presión (bar)']=media.loc[i,'Presion deposito (bar)']
                    tabla_propiedades.loc['4','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H",tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
                    tabla_propiedades.loc['4','Temperatura (°C)']=(CP.PropsSI("T", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))-273.15
                    tabla_propiedades.loc['4','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2")
                    tabla_propiedades.loc['4','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
                    tabla_propiedades.loc['4','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H",tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))/1000

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

                    tabla_propiedades.loc['5','Presión (bar)']=media.loc[i,'Presion deposito (bar)']
                    tabla_propiedades.loc['5','Temperatura (°C)']=(CP.PropsSI("T", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))-273.15
                    tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D", tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000
                    tabla_propiedades.loc['5','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",tabla_propiedades.loc['5','Presión (bar)']*(10**5) , "D",tabla_propiedades.loc['5','Densidad (Kg/m^3)'], "CO2"))/1000

                    tabla_propiedades.loc['4s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']
                    tabla_propiedades.loc['4s','Presión (bar)']=media.loc[i,'Presion deposito (bar)']
                    tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "S",tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
                    tabla_propiedades.loc['4s','Temperatura (°C)']=(CP.PropsSI("T", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
                    tabla_propiedades.loc['4s','Caudal másico (Kg/s)']=0
                    tabla_propiedades.loc['4s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "S", tabla_propiedades.loc['3','Entropía (kJ/Kg·K)']*1000, "CO2")

                    tabla_propiedades.loc['6s','Entropía (kJ/Kg·K)']=tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']
                    tabla_propiedades.loc['6s','Presión (bar)']=media.loc[i,'Presion condensacion (bar)']
                    tabla_propiedades.loc['6s','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "S",tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))/1000
                    tabla_propiedades.loc['6s','Temperatura (°C)']=(CP.PropsSI("T", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2"))-273.15
                    tabla_propiedades.loc['6s','Caudal másico (Kg/s)']=0
                    tabla_propiedades.loc['6s','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion condensacion (bar)']*(10**5) , "S", tabla_propiedades.loc['5','Entropía (kJ/Kg·K)']*1000, "CO2")

                    tabla_propiedades.loc['4','Entalpía (kJ/Kg)']=tabla_propiedades.loc['3','Entalpía (kJ/Kg)']+(tabla_propiedades.loc['4s','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])/(R_isentropico/100)
                    tabla_propiedades.loc['4','Presión (bar)']=media.loc[i,'Presion deposito (bar)']
                    tabla_propiedades.loc['4','Entalpía (kJ/Kg)']=(CP.PropsSI("H", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H",tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))/1000
                    tabla_propiedades.loc['4','Temperatura (°C)']=(CP.PropsSI("T", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))-273.15
                    tabla_propiedades.loc['4','Densidad (Kg/m^3)']=CP.PropsSI("D", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H", tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2")
                    tabla_propiedades.loc['4','Caudal másico (Kg/s)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']
                    tabla_propiedades.loc['4','Entropía (kJ/Kg·K)']=(CP.PropsSI("S", "P",media.loc[i,'Presion deposito (bar)']*(10**5) , "H",tabla_propiedades.loc['4','Entalpía (kJ/Kg)']*1000, "CO2"))/1000

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

            if 'Diagramas P-H y T-S' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:
                diagrama.data = []
                #Diagramas ph y ts

                #Curvas de saturación
                presion = np.linspace(CP.PropsSI('CO2', 'ptriple'), CP.PropsSI('CO2', 'pcrit') , 1000)
                h_liq = [CP.PropsSI('H', 'P', pi, 'Q', 0, "CO2")/1000 for pi in presion]  
                h_vap = [CP.PropsSI('H', 'P', pi, 'Q', 1, "CO2")/1000 for pi in presion]  
                s_liq = [CP.PropsSI('S', 'P', pi, 'Q', 0, "CO2")/1000 for pi in presion]  
                s_vap = [CP.PropsSI('S', 'P', pi, 'Q', 1, "CO2")/1000 for pi in presion]  
                T_liq = [CP.PropsSI('T', 'P', pi, 'Q', 0, "CO2")-273.15 for pi in presion]  
                T_vap = [CP.PropsSI('T', 'P', pi, 'Q', 1, "CO2")-273.15 for pi in presion]  

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

                diagrama.add_trace(go.Scatter(x=h_liq, y=(presion/1e5),mode='lines', name='Líquido saturado', line=dict(color='blue'),hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
                diagrama.add_trace(go.Scatter(x=h_vap, y=(presion/1e5),mode='lines', name='Vapor saturado', line=dict(color='red'),hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1) 
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ph_3['x'],y=puntos_ciclo_ph_3['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ph_2['x'],y=puntos_ciclo_ph_2['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ph['x'],y=puntos_ciclo_ph['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ph_4['x'],y=puntos_ciclo_ph_4['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ph_5['x'],y=puntos_ciclo_ph_5['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Presión: %{y:.2f} bar<br>Entalpía: %{x:.2f} kJ/kg"), row=1, col=1)
                #presion_ticks=[0,10,20,30,40,50,60,70,80]
                #fig.update_yaxes(title_text="Presión (bar)", type="log",tickvals=presion_ticks,ticktext=[f"{p:.0f}" for p in presion_ticks],range=[np.log10(CP.PropsSI('CO2', 'ptriple')/1e5), np.log10(CP.PropsSI('CO2', 'pcrit')/1e5)], row=1, col=1)
                diagrama.update_yaxes(title_text="Presión (bar)", row=1, col=1,showgrid=False,mirror=False,zeroline=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))
                diagrama.update_xaxes(title_text="Entalpía (kJ/Kg)", row=1, col=1,showgrid=False,mirror=False,zeroline=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))

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


                diagrama.add_trace(go.Scatter(x=s_liq, y=T_liq,mode='lines', name='Líquido saturado', line=dict(color='blue'), showlegend=False,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=s_vap, y=T_liq,mode='lines', name='Vapor saturado', line=dict(color='red'), showlegend=False,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ts_3['x'],y=puntos_ciclo_ts_3['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ts_6['x'],y=puntos_ciclo_ts_6['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ts_2['x'],y=puntos_ciclo_ts_2['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ts['x'],y=puntos_ciclo_ts['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ts_4['x'],y=puntos_ciclo_ts_4['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ts_5['x'],y=puntos_ciclo_ts_5['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='dash'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ts_7['x'],y=puntos_ciclo_ts_7['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=puntos_ciclo_ts_8['x'],y=puntos_ciclo_ts_8['y'],mode='lines+markers',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)

                diagrama.add_trace(go.Scatter(x=entropia_isobara_alta/1000,y=temperatura_isobara_alta,mode='lines',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)
                diagrama.add_trace(go.Scatter(x=entropia_isobara_intermedia/1000,y=temperatura_isobara_intermedia,mode='lines',name='Ciclo',line=dict(color='black', width=2, dash='solid'),marker=dict(size=7, color='black'),showlegend=True,hovertemplate="Temperatura: %{y:.2f} °C<br>Entropía: %{x:.2f} kJ/Kg·K"), row=1, col=2)



                diagrama.update_yaxes(title_text="Temperatura (°C)", row=1, col=2,showgrid=False,zeroline=False,mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))
                diagrama.update_xaxes(title_text="Entropía (kJ/Kg·K)", row=1, col=2,showgrid=False,zeroline=False,mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(font=dict(color='black')))

                # Ajustes finales
                diagrama.update_layout(height=600,width=1200,title_text="Diagramas dinámicos del ciclo",title_font=dict(size=16,family='Arial'),hovermode="closest",showlegend=False)
                diagrama_placeholder.plotly_chart(diagrama, use_container_width=True)

            if 'Diagramas P-H y T-S' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:

                tabla_propiedades.index.name = "Puntos"
                tabla_placeholder_propiedades.dataframe(tabla_propiedades,height=400,use_container_width=True,hide_index=False)

#
            if 'COP' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:

                media.loc[i,'Consumo eléctrico (compresor)']=media.loc[i,'Potencia total (W)']/1000
                media.loc[i,'Potencia frigorífica (evaporadores)']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['1','Entalpía (kJ/Kg)']-tabla_propiedades.loc['10','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['2','Entalpía (kJ/Kg)']-tabla_propiedades.loc['1','Entalpía (kJ/Kg)'])
                media.loc[i,'Potencia ideal (compresor)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']*(tabla_propiedades.loc['4','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])
                media.loc[i,'Potencia cedida (gas-cooler)']=tabla_propiedades.loc['6','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['7','Entalpía (kJ/Kg)'])
                if media.loc[i,'Rele compresor (on/off)']!=0:
                    media.loc[i,'COP (EER)']=media.loc[i,'Potencia frigorífica (evaporadores)']/(media.loc[i,'Potencia total (W)']/1000)
                    media.loc[i,'COP (BC)']=media.loc[i,'Potencia cedida (gas-cooler)']/(media.loc[i,'Potencia total (W)']/1000)
                else:
                    media.loc[i,'COP (EER)']=0
                    media.loc[i,'COP (BC)']=0                    

                df_actual_cop = media.loc[:i + 1,['COP (EER)','COP (BC)','Tiempo','Indice']]
                df_melted_cop = df_actual_cop.melt(id_vars=['Tiempo','Indice'], var_name='Variable', value_name='Valor')

                fig_cop = px.line(
                    df_melted_cop,
                    x='Tiempo',
                    y='Valor',
                    color='Variable',
                    labels={'Tiempo': 'Tiempo (minutos)', 'Valor': 'Valor'},
                    title='Gráfica dinámica de coeficientes de rendimiento',custom_data=['Indice'])
                fig_cop.update_traces(
                    hovertemplate="Tiempo: %{x}<br>Valor: %{y}<br>Hora: %{customdata[0]}<br>Variable: %{fullData.name}<extra></extra>"
                )
                fig_cop.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',range=[0,3],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
                grafica_cop.plotly_chart(fig_cop)


            if 'Potencias del ciclo' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:

                media.loc[i,'Consumo eléctrico (compresor) (kW)']=media.loc[i,'Potencia total (W)']/1000
                media.loc[i,'Potencia frigorífica (evaporadores) (kW)']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['1','Entalpía (kJ/Kg)']-tabla_propiedades.loc['10','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['2','Entalpía (kJ/Kg)']-tabla_propiedades.loc['1','Entalpía (kJ/Kg)'])
                media.loc[i,'Potencia ideal (compresor) (kW)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']*(tabla_propiedades.loc['4','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])
                media.loc[i,'Potencia cedida (gas-cooler) (kW)']=tabla_propiedades.loc['6','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['7','Entalpía (kJ/Kg)'])                
                df_actual_potencias = media.loc[:i + 1,['Consumo eléctrico (compresor) (kW)','Potencia frigorífica (evaporadores) (kW)','Potencia ideal (compresor) (kW)','Potencia cedida (gas-cooler) (kW)','Tiempo','Indice']]
                df_melted_potencias = df_actual_potencias.melt(id_vars=['Tiempo','Indice'], var_name='Variable', value_name='Valor')

                fig_potencias= px.line(
                    df_melted_potencias,
                    x='Tiempo',
                    y='Valor',
                    color='Variable',
                    labels={'Tiempo': 'Tiempo (minutos)', 'Valor': 'Valor'},
                    title='Gráfica dinámica de coeficientes de rendimiento',custom_data=['Indice'])
                fig_potencias.update_traces(
                    hovertemplate="Tiempo: %{x}<br>Valor: %{y}<br>Hora: %{customdata[0]}<br>Variable: %{fullData.name}<extra></extra>"
                )
                fig_potencias.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
                grafica_potencias.plotly_chart(fig_potencias)

            if 'COP' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:

                media.loc[i,'Consumo eléctrico (compresor)']=media.loc[i,'Potencia total (W)']/1000
                media.loc[i,'Potencia frigorífica (evaporadores)']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['1','Entalpía (kJ/Kg)']-tabla_propiedades.loc['10','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['2','Entalpía (kJ/Kg)']-tabla_propiedades.loc['1','Entalpía (kJ/Kg)'])
                media.loc[i,'Potencia ideal (compresor)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']*(tabla_propiedades.loc['4','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])
                media.loc[i,'Potencia cedida (gas-cooler)']=tabla_propiedades.loc['6','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['7','Entalpía (kJ/Kg)'])
                if media.loc[i,'Rele compresor (on/off)']!=0:
                    media.loc[i,'COP (EER)']=media.loc[i,'Potencia frigorífica (evaporadores)']/(media.loc[i,'Potencia total (W)']/1000)
                    media.loc[i,'COP (BC)']=media.loc[i,'Potencia cedida (gas-cooler)']/(media.loc[i,'Potencia total (W)']/1000)
                else:
                    media.loc[i,'COP (EER)']=0
                    media.loc[i,'COP (BC)']=0        

                # Actualizar la tabla con los datos actuales
                hora_actual = media.loc[i]["Indice"]
                fila_actual = media.loc[i,['COP (EER)','COP (BC)']].to_frame().T
                fila_actual.index = [hora_actual]
                tabla_datos_cop = pd.concat([tabla_datos_cop, fila_actual])
                # Mostrar la tabla actualizada
                tabla_placeholder_cop.dataframe(tabla_datos_cop,use_container_width=True)

            if 'Potencias del ciclo' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:

                media.loc[i,'Consumo eléctrico (compresor) (kW)']=media.loc[i,'Potencia total (W)']/1000
                media.loc[i,'Potencia frigorífica (evaporadores) (kW)']=tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['1','Entalpía (kJ/Kg)']-tabla_propiedades.loc['10','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['2','Caudal másico (Kg/s)']*(tabla_propiedades.loc['2','Entalpía (kJ/Kg)']-tabla_propiedades.loc['1','Entalpía (kJ/Kg)'])
                media.loc[i,'Potencia ideal (compresor) (kW)']=tabla_propiedades.loc['3','Caudal másico (Kg/s)']*(tabla_propiedades.loc['4','Entalpía (kJ/Kg)']-tabla_propiedades.loc['3','Entalpía (kJ/Kg)'])+tabla_propiedades.loc['5','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['5','Entalpía (kJ/Kg)'])
                media.loc[i,'Potencia cedida (gas-cooler) (kW)']=tabla_propiedades.loc['6','Caudal másico (Kg/s)']*(tabla_propiedades.loc['6','Entalpía (kJ/Kg)']-tabla_propiedades.loc['7','Entalpía (kJ/Kg)'])                

                # Actualizar la tabla con los datos actuales
                hora_actual = media.loc[i]["Indice"]
                fila_actual = media.loc[i,['Consumo eléctrico (compresor) (kW)','Potencia frigorífica (evaporadores) (kW)','Potencia ideal (compresor) (kW)','Potencia cedida (gas-cooler) (kW)']].to_frame().T
                fila_actual.index = [hora_actual]
                tabla_datos_potencias = pd.concat([tabla_datos_potencias, fila_actual])
                # Mostrar la tabla actualizada
                tabla_placeholder_potencias.dataframe(tabla_datos_potencias,use_container_width=True)


            if 'Flujos másicos' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:

                if tabla_propiedades.loc['7','Caudal másico (Kg/s)']<0:
                    media.loc[i,'Flujo másico (refrigerante bifásico) (Kg/s)']=0
                else:
                    media.loc[i,'Flujo másico (refrigerante bifásico) (Kg/s)']=tabla_propiedades.loc['7','Caudal másico (Kg/s)']
                if tabla_propiedades.loc['11','Caudal másico (Kg/s)']<0:
                    media.loc[i,'Flujo másico (refrigerante vapor saturado) (Kg/s)']=0
                else:
                    media.loc[i,'Flujo másico (refrigerante vapor saturado) (Kg/s)']=tabla_propiedades.loc['11','Caudal másico (Kg/s)']
                if tabla_propiedades.loc['9','Caudal másico (Kg/s)']<0:
                    media.loc[i,'Flujo másico (refrigerante líquido saturado) (Kg/s)']=0
                else:
                    media.loc[i,'Flujo másico (refrigerante líquido saturado) (Kg/s)']=tabla_propiedades.loc['9','Caudal másico (Kg/s)']
                
                df_actual_flujos = media.loc[:i + 1,['Flujo másico (refrigerante bifásico) (Kg/s)','Flujo másico (refrigerante vapor saturado) (Kg/s)','Flujo másico (refrigerante líquido saturado) (Kg/s)','Tiempo','Indice']]
                df_melted_flujos = df_actual_flujos.melt(id_vars=['Tiempo','Indice'], var_name='Variable', value_name='Valor')

                fig_flujos= px.line(
                    df_melted_flujos,
                    x='Tiempo',
                    y='Valor',
                    color='Variable',
                    labels={'Tiempo': 'Tiempo (minutos)', 'Valor': 'Valor'},
                    title='Gráfica dinámica de flujos másicos',custom_data=['Indice'])
                fig_flujos.update_traces(
                    hovertemplate="Tiempo: %{x}<br>Valor: %{y}<br>Hora: %{customdata[0]}<br>Variable: %{fullData.name}<extra></extra>"
                )
                fig_flujos.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
                grafica_flujos.plotly_chart(fig_flujos)

            if 'Flujos másicos' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:
                if tabla_propiedades.loc['7','Caudal másico (Kg/s)']<0:
                    media.loc[i,'Flujo másico (refrigerante bifásico) (Kg/s)']=0
                else:
                    media.loc[i,'Flujo másico (refrigerante bifásico) (Kg/s)']=tabla_propiedades.loc['7','Caudal másico (Kg/s)']
                if tabla_propiedades.loc['11','Caudal másico (Kg/s)']<0:
                    media.loc[i,'Flujo másico (refrigerante vapor saturado) (Kg/s)']=0
                else:
                    media.loc[i,'Flujo másico (refrigerante vapor saturado) (Kg/s)']=tabla_propiedades.loc['11','Caudal másico (Kg/s)']
                if tabla_propiedades.loc['9','Caudal másico (Kg/s)']<0:
                    media.loc[i,'Flujo másico (refrigerante líquido saturado) (Kg/s)']=0
                else:
                    media.loc[i,'Flujo másico (refrigerante líquido saturado) (Kg/s)']=tabla_propiedades.loc['9','Caudal másico (Kg/s)']
                # Actualizar la tabla con los datos actuales
                hora_actual = media.loc[i]["Indice"]
                fila_actual = media.loc[i,['Flujo másico (refrigerante bifásico) (Kg/s)','Flujo másico (refrigerante vapor saturado) (Kg/s)','Flujo másico (refrigerante líquido saturado) (Kg/s)']].to_frame().T
                fila_actual.index = [hora_actual]
                tabla_datos_flujos = pd.concat([tabla_datos_flujos, fila_actual])
                # Mostrar la tabla actualizada
                tabla_placeholder_flujos.dataframe(tabla_datos_flujos,use_container_width=True)

            if 'Rendimientos del compresor' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:

                if R_volumetrico_baja_teorico>100:
                    media.loc[i,'Rendimiento volumétrico (primera etapa de compresión) (%)']=100

                else:
                    media.loc[i,'Rendimiento volumétrico (primera etapa de compresión) (%)']=R_volumetrico_baja_teorico
                media.loc[i,'Rendimiento isentrópico (primera y segunda etapa de compresión) (%)']=R_isentropico
                media.loc[i,'Rendimiento volumétrico (segunda estapa de compresión) (%)']=R_volumetrico_alta_teorico

                df_actual_rendimientos = media.loc[:i + 1,['Rendimiento isentrópico (primera y segunda etapa de compresión) (%)','Rendimiento volumétrico (primera etapa de compresión) (%)','Rendimiento volumétrico (segunda estapa de compresión) (%)','Tiempo','Indice']]
                df_melted_rendimientos = df_actual_rendimientos.melt(id_vars=['Tiempo','Indice'], var_name='Variable', value_name='Valor')

                fig_rendimientos= px.line(
                    df_melted_rendimientos,
                    x='Tiempo',
                    y='Valor',
                    color='Variable',
                    labels={'Tiempo': 'Tiempo (minutos)', 'Valor': 'Valor'},
                    title='Gráfica dinámica de rendimientos del compresor',custom_data=['Indice'])
                fig_rendimientos.update_traces(
                    hovertemplate="Tiempo: %{x}<br>Valor: %{y}<br>Hora: %{customdata[0]}<br>Variable: %{fullData.name}<extra></extra>"
                )
                fig_rendimientos.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
                grafica_rendimientos.plotly_chart(fig_rendimientos)

            if 'Rendimientos del compresor' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:

                if R_volumetrico_baja_teorico>100:
                    media.loc[i,'Rendimiento volumétrico (primera etapa de compresión) (%)']=100

                else:
                    media.loc[i,'Rendimiento volumétrico (primera etapa de compresión) (%)']=R_volumetrico_baja_teorico
                media.loc[i,'Rendimiento isentrópico (primera y segunda etapa de compresión) (%)']=R_isentropico
                media.loc[i,'Rendimiento volumétrico (segunda estapa de compresión) (%)']=R_volumetrico_alta_teorico

                # Actualizar la tabla con los datos actuales
                hora_actual = media.loc[i]["Indice"]
                fila_actual = media.loc[i,['Rendimiento volumétrico (primera etapa de compresión) (%)','Rendimiento volumétrico (segunda estapa de compresión) (%)','Rendimiento isentrópico (primera y segunda etapa de compresión) (%)']].to_frame().T
                fila_actual.index = [hora_actual]
                tabla_datos_rendimientos = pd.concat([tabla_datos_rendimientos, fila_actual])
                # Mostrar la tabla actualizada
                tabla_placeholder_rendimientos.dataframe(tabla_datos_rendimientos,use_container_width=True)

            if 'Caracterización de los evaporadores' in indicadores_termodinamicos and 'Gráfico de líneas' in tipo_grafico_diferido:

                media.loc[i,'Efectividad (evaporador 1) (%)']=round((media.loc[i,'Temperatura camara (evaporador 1) (°C)']-media.loc[i,'Temperatura desescarche (evaporador 1) (°C)'])*100/(media.loc[i,'Temperatura camara (evaporador 1) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),2)
                media.loc[i,'Efectividad (evaporador 2) (%)']=round((media.loc[i,'Temperatura camara (evaporador 2) (°C)']-media.loc[i,'Temperatura desescarche (evaporador 2) (°C)'])*100/(media.loc[i,'Temperatura camara (evaporador 2) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),2)
                media.loc[i,'Salto térmico (entrada - evaporador 1) (K)']=media.loc[i,'Temperatura camara (evaporador 1) (°C)']-tabla_propiedades.loc['2','Temperatura (°C)']
                media.loc[i,'Salto térmico (salida - evaporador 1) (K)']=media.loc[i,'Temperatura desescarche (evaporador 1) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']
                media.loc[i,'Salto térmico (entrada - evaporador 2) (K)']=media.loc[i,'Temperatura camara (evaporador 2) (°C)']-tabla_propiedades.loc['2','Temperatura (°C)']
                media.loc[i,'Salto térmico (salida - evaporador 2) (K)']=media.loc[i,'Temperatura desescarche (evaporador 2) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']

                df_actual_efectividad = media.loc[:i + 1,['Efectividad (evaporador 1) (%)','Efectividad (evaporador 2) (%)','Tiempo','Indice']]
                df_melted_efectividad = df_actual_efectividad.melt(id_vars=['Tiempo','Indice'], var_name='Variable', value_name='Valor')

                fig_efectividad= px.line(
                    df_melted_efectividad,
                    x='Tiempo',
                    y='Valor',
                    color='Variable',
                    labels={'Tiempo': 'Tiempo (minutos)', 'Valor': 'Valor'},
                    title='Gráfica dinámica de efectividad',custom_data=['Indice'])
                fig_efectividad.update_traces(
                    hovertemplate="Tiempo: %{x}<br>Valor: %{y}<br>Hora: %{customdata[0]}<br>Variable: %{fullData.name}<extra></extra>"
                )
                fig_efectividad.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
                grafica_efectividad.plotly_chart(fig_efectividad)

                df_actual_saltos = media.loc[:i + 1,['Salto térmico (entrada - evaporador 1) (K)','Salto térmico (salida - evaporador 1) (K)','Salto térmico (entrada - evaporador 2) (K)','Salto térmico (salida - evaporador 2) (K)','Tiempo','Indice']]
                df_melted_saltos = df_actual_saltos.melt(id_vars=['Tiempo','Indice'], var_name='Variable', value_name='Valor')

                fig_saltos= px.line(
                    df_melted_saltos,
                    x='Tiempo',
                    y='Valor',
                    color='Variable',
                    labels={'Tiempo': 'Tiempo (minutos)', 'Valor': 'Valor'},
                    title='Gráfica dinámica de saltos térmicos',custom_data=['Indice'])
                fig_saltos.update_traces(
                    hovertemplate="Tiempo: %{x}<br>Valor: %{y}<br>Hora: %{customdata[0]}<br>Variable: %{fullData.name}<extra></extra>"
                )
                fig_saltos.update_layout(
                    width=None,
                    height=500,
                    legend=dict(orientation='h', yanchor='bottom', y=-0.4,title_font_color='black'),
                    xaxis=dict(showgrid=True, gridcolor='lightgray',range=[0,df_ampliado_analogico['Tiempo'].max()],mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Tiempo (minutos)', font=dict(color='black'))),
                    yaxis=dict(showgrid=True,gridcolor='lightgray',mirror=False,linecolor='black',tickfont=dict(color='black'),title=dict(text='Valor', font=dict(color='black'))))
                grafica_saltos.plotly_chart(fig_saltos)

            if 'Caracterización de los evaporadores' in indicadores_termodinamicos and 'Tabla' in tipo_grafico_diferido:
                media.loc[i,'Efectividad (evaporador 1) (%)']=round((media.loc[i,'Temperatura camara (evaporador 1) (°C)']-media.loc[i,'Temperatura desescarche (evaporador 1) (°C)'])*100/(media.loc[i,'Temperatura camara (evaporador 1) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),2)
                media.loc[i,'Efectividad (evaporador 2) (%)']=round((media.loc[i,'Temperatura camara (evaporador 2) (°C)']-media.loc[i,'Temperatura desescarche (evaporador 2) (°C)'])*100/(media.loc[i,'Temperatura camara (evaporador 2) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']),2)
                media.loc[i,'Salto térmico (entrada - evaporador 1) (K)']=media.loc[i,'Temperatura camara (evaporador 1) (°C)']-tabla_propiedades.loc['2','Temperatura (°C)']
                media.loc[i,'Salto térmico (salida - evaporador 1) (K)']=media.loc[i,'Temperatura desescarche (evaporador 1) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']
                media.loc[i,'Salto térmico (entrada - evaporador 2) (K)']=media.loc[i,'Temperatura camara (evaporador 2) (°C)']-tabla_propiedades.loc['2','Temperatura (°C)']
                media.loc[i,'Salto térmico (salida - evaporador 2) (K)']=media.loc[i,'Temperatura desescarche (evaporador 2) (°C)']-tabla_propiedades.loc['1','Temperatura (°C)']

                # Actualizar la tabla con los datos actuales
                hora_actual = media.loc[i]["Indice"]
                fila_actual = media.loc[i,['Efectividad (evaporador 1) (%)','Efectividad (evaporador 2) (%)','Salto térmico (entrada - evaporador 1) (K)','Salto térmico (salida - evaporador 1) (K)','Salto térmico (entrada - evaporador 2) (K)','Salto térmico (salida - evaporador 2) (K)']].to_frame().T
                fila_actual.index = [hora_actual]
                tabla_datos_evaporadores = pd.concat([tabla_datos_evaporadores, fila_actual])
                # Mostrar la tabla actualizada
                tabla_placeholder_evaporadores.dataframe(tabla_datos_evaporadores,use_container_width=True)







        # Esperar un momento antes de la siguiente actualización
        sleep(velocidad_reproduccion)