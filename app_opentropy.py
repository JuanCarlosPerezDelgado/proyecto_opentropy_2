from datetime import datetime, timedelta         
import pandas as pd
 
import numpy as np
import streamlit as st
import altair as alt
from time import sleep
import streamlit_option_menu
from streamlit_option_menu import option_menu
import plotly.express as px
import webbrowser

#Importar funciones
from busquedaensayo import busqueda
from busquedaensayo import ensayo
from ensayoendiferido import representacion_grafico
from laboratorio_virtual import imagen_360
from datos_continuo import datos_continuo
from puntos_clave import busqueda_puntos_compresor
from puntos_clave import busqueda_puntos_variable
from puntos_clave import busqueda_puntos_control
from puntos_clave import calculos_termodinamicos
from modelotermodinamico import calculo_modelo

#from puntos_clave import calculos_puntos_compresor

# Configuración de la páginas
st.set_page_config(layout="wide")

# Configuración de la barra lateral
with st.sidebar:

    # Menú principal
    menu= option_menu(menu_title=None,  
        options=["Laboratorio Virtual", "Información",'---','Datos en Continuo','---',"Datos en Histórico","Herramientas"],
        default_index=0,
         styles={"container": {"padding": "5px", "background-color": "#ffffff"},
        "icon": {"color": "orange", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
        "nav-link-selected": {"background-color": "#03617E"},})

# Mostrar contenido según la opción seleccionada
if menu == 'Laboratorio Virtual':

    #Título
    st.markdown("<h2 style='text-align: center;'>Equipo para cámaras de refrigeración y congelación de CO2 transcrítico</h2>",unsafe_allow_html=True)

    # Salto de línea
    st.markdown("<br>", unsafe_allow_html=True) 

    #Función 360 grados
    imagen_360()

elif menu == "Información":

    #Título
    st.markdown("<h2 style='text-align: center;'>Equipo para cámaras de refrigeración y congelación de CO2 transcrítico</h2>",unsafe_allow_html=True)


elif menu == "Datos en Continuo":

    #Título
    st.markdown("<h2 style='text-align: center;'>Datos en Continuo</h2>",unsafe_allow_html=True)

    # Salto de línea
    st.markdown("<br>", unsafe_allow_html=True) 

    #Información
    st.markdown("<p style='font-size: 18px;'><strong>Selecciona las variables, el tipo de gráfico y el intervalo de visualización</strong></p>", unsafe_allow_html=True)

    variables_analizador_redes = st.multiselect('Analizador de redes',["Potencia total (W)","Energia total (kWh)"])
    variables_evaporador_04= st.multiselect('Evaporador 1',["Temperatura camara (evaporador 1) (°C)","Temperatura desescarche (evaporador 1) (°C)","Rele desescarche (evaporador 1) (on/off)","Rele ventilador (evaporador 1) (on/off)","Rele valvula (evaporador 1) (on/off)","Estado desescarche (evaporador 1) (on/off)","Estado dispositivo (evaporador 1) (on/off)"])
    variables_valvula_expansion_05 = st.multiselect('Válvula expansion 1',["Presion de baja (valvula expansion 1) (bar)","Temperatura aspiracion (valvula expansion 1) (°C)","Recalentamiento (valvula expansion 1) (K)","Apertura valvula (valvula expansion 1) (%)","Estado valvula (valvula expansion 1) (on/off)"])
    variables_evaporador_06= st.multiselect('Evaporador 2',["Temperatura camara (evaporador 2) (°C)","Temperatura desescarche (evaporador 2) (°C)","Rele desescarche (evaporador 2) (on/off)","Rele ventilador (evaporador 2) (on/off)","Rele valvula (evaporador 2) (on/off)","Estado desescarche (evaporador 2) (on/off)","Estado dispositivo (evaporador 2) (on/off)"])
    variables_valvula_expansion_07 = st.multiselect('Válvula expansion 2',["Presion de baja (valvula expansion 2) (bar)","Temperatura aspiracion (valvula expansion 2) (°C)","Recalentamiento (valvula expansion 2) (K)","Apertura valvula (valvula expansion 2) (%)","Estado valvula (valvula expansion 2) (on/off)"])
    variables_equipo = st.multiselect('Central transcrítica y gas-cooler',['Presion evaporacion (bar)','Temperatura evaporacion (°C)',"Presion condensacion (bar)","Temperatura condensacion (°C)","Presion deposito (bar)","Temperatura deposito (°C)","Temperatura exterior (°C)","Temperatura salida gas cooler (°C)","Temperatura aspiracion (°C)","Temperatura descarga (°C)","Temperatura liquido (°C)","Potencia compresor (%)","Potencia ventilador gas-cooler (%)","Apertura valvula by-pass (%)","Apertura valvula alta presion (%)","Rele compresor (on/off)"])
    tipo_grafico = st.multiselect('Tipo de gráfico',['Scada','Gráfico de líneas','Tabla'])
    intervalo_visualizacion = st.slider("Intervalo de visualización (minutos):",min_value=1,max_value=30,value=10,step=1)
    lista_variables=variables_analizador_redes+variables_evaporador_04+variables_valvula_expansion_05+variables_evaporador_06+variables_valvula_expansion_07+variables_equipo
    

    # Salto de línea
    st.markdown("<br>", unsafe_allow_html=True) 
    # Botón para iniciar la actualización dinámica

    if st.button("Iniciar visualización"):

        if not lista_variables or not tipo_grafico:
            st.warning("Selecciona al menos una variable y un tipo de gráfico")

        else:
            
            #Barra de progreso
            with st.spinner("Cargando..."):

                # Salto de línea
                st.markdown("<br>", unsafe_allow_html=True)

                #Visualización en continuo
                try:
                    datos_continuo(lista_variables,tipo_grafico,intervalo_visualizacion)
                except:
                    st.error("Problema de conectividad con el servidor")

elif menu == "Datos en Histórico":

    #Título
    st.markdown("<h2 style='text-align: center;'>Gestión de Datos de Funcionamiento</h2>",unsafe_allow_html=True)

    # Salto de línea
    st.markdown("<br>", unsafe_allow_html=True) 

    #Información
    st.markdown("<p style='font-size: 18px;'><strong>Selecciona el tipo de instalación</strong></p>", unsafe_allow_html=True)

    # Widgets de configuración
    instalacion = st.selectbox('Instalaciones disponibles',["Equipo para cámaras de refrigeración y congelación de CO2 transcrítico (Escuela de Ingeniería Industriales - Universidad de Málaga)", 
            "Equipo compacto monoblock para cámaras de refrigeración y congelación de R-290 (I.E.S Heliópolis - Sevilla)", 
            "Sistema de refrigeración solar compacto (I.E.S Marqués de Comares - Lucena(Córdoba))"])
    
    if instalacion == "Equipo compacto monoblock para cámaras de refrigeración y congelación de R-290 (I.E.S Heliópolis - Sevilla)" or instalacion == "Sistema de refrigeración solar compacto (I.E.S Marqués de Comares - Lucena(Córdoba))":

        st.info('Si quiere ser redirigido a la plataforma de la instalación seleccionada pulse sobre el botón')
        # Botón para redireccionar
        if st.button("Instalación"):
            webbrowser.open_new_tab("https://opentropy.com/")

    else: 

        # Guardar la lista de ensayos y los intervalos en el estado de la aplicación
        st.session_state.instalacion = instalacion

    # Salto de línea
    st.markdown("<br>", unsafe_allow_html=True)

    #Información
    st.markdown("<p style='font-size: 18px;'><strong>Selecciona el rango de fechas y duración de los ensayos</strong></p>", unsafe_allow_html=True)

    # Widgets de configuración
    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha de inicio", value=datetime.today())
    with col2:
        fecha_fin = st.date_input("Fecha de fin", value=datetime.today())

    # Validar que la fecha de fin sea mayor o igual que la fecha de inicio
    if fecha_inicio > fecha_fin:
        st.error("La fecha de fin debe ser mayor o igual que la fecha de inicio.")

    # Widgets de configuración
    duracion_minutos = st.slider("Duración mínima de los ensayos (minutos):",min_value=2,max_value=300,value=15,step=1)

    # Salto de línea
    st.markdown("<br>", unsafe_allow_html=True) 

    # Inicializar el estado de la aplicación para que no se active el selectbox de ensayos disponibles
    if "lista_ensayos" not in st.session_state:
        st.session_state.lista_ensayos = []

    # Botón para iniciar la búsqueda de ensayos
    if st.button("Iniciar búsqueda de ensayos"):
        
        #Barra de progreso
        with st.spinner("Buscando ensayos..."):  

            #Función de búsqueda
            lista_ensayos,intervalos_ensayos,df_analizador_redes,df_equipo,df_evaporador_04,df_valvula_expansion_05,df_evaporador_06,df_valvula_expansion_07=busqueda(instalacion,fecha_inicio,fecha_fin,duracion_minutos)

            #Verificar si la lista de ensayos está vacía
            if not lista_ensayos:
                st.error('Ensayos no encontrados')
            else:
                # Mensaje de éxito o error
                st.success("Búsqueda completada")

            # Guardar la lista de ensayos y los intervalos en el estado de la aplicación
                st.session_state.lista_ensayos = lista_ensayos
                st.session_state.intervalos_ensayos = intervalos_ensayos
                st.session_state.df_analizador_redes = df_analizador_redes
                st.session_state.df_equipo = df_equipo
                st.session_state.df_evaporador_04 = df_evaporador_04
                st.session_state.df_valvula_expansion_05 = df_valvula_expansion_05
                st.session_state.df_evaporador_06 = df_evaporador_06
                st.session_state.df_valvula_expansion_07 = df_valvula_expansion_07

    # Mostrar el selectbox si hay ensayos disponibles
    if st.session_state.lista_ensayos:

        # Salto de línea
        st.markdown("<br>", unsafe_allow_html=True)

        # Información
        st.markdown("<p style='font-size: 18px;'><strong>Selecciona el ensayo</strong></p>", unsafe_allow_html=True)

        # Widgets de selección del ensayo
        ensayo_seleccionado = st.selectbox('Ensayos disponibles',st.session_state.lista_ensayos)

        # Guardar el ensayo seleccionado en el estado de la aplicación
        st.session_state.ensayo_seleccionado = ensayo_seleccionado

        # Salto de línea
        st.markdown("<br>", unsafe_allow_html=True)

        # Botón para iniciar la carga de los datos
        if st.button("Iniciar carga de los datos para las herramientas de análisis"):

            #Barra de progreso
            with st.spinner("Cargando datos..."):

                #Función de carga de los datos
                df_analizador_redes_ensayo,df_equipo_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo=ensayo(st.session_state.ensayo_seleccionado,st.session_state.lista_ensayos,st.session_state.intervalos_ensayos,st.session_state.df_analizador_redes,st.session_state.df_equipo,st.session_state.df_evaporador_04,st.session_state.df_valvula_expansion_05,st.session_state.df_evaporador_06,st.session_state.df_valvula_expansion_07)

                #Verificar si la lista de ensayos está vacía
                if df_equipo_ensayo.empty:
                    st.error('Datos no cargados')
                else:
                    st.success("Datos cargados")

                # Guardar los dataframe en el estado de la aplicación
                st.session_state.df_analizador_redes_ensayo = df_analizador_redes_ensayo
                st.session_state.df_equipo_ensayo = df_equipo_ensayo
                st.session_state.df_evaporador_04_ensayo = df_evaporador_04_ensayo
                st.session_state.df_valvula_expansion_05_ensayo = df_valvula_expansion_05_ensayo
                st.session_state.df_evaporador_06_ensayo = df_evaporador_06_ensayo
                st.session_state.df_valvula_expansion_07_ensayo = df_valvula_expansion_07_ensayo



elif menu == "Herramientas":

    menu_herramientas = option_menu(
        menu_title=None,  
        options=["Simulación en Diferido","Estudio de Puntos Clave",'Modelo Termodinámico'],
        #options=["Simulación en Diferido", "Análisis Temporal","Estudio de Puntos Clave",'Modelo Termodinámico'],
        default_index=0,
        orientation='horizontal',
        styles={
        "container": {"padding": "5px", "background-color": "#ffffff"},
        "icon": {"color": "orange", "font-size": "18px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
        "nav-link-selected": {"background-color": "#03617E"},
    }
    )

    if menu_herramientas == 'Simulación en Diferido':

        #Título
        #st.markdown("<h2 style='text-align: center;'>Simulación en Diferido</h2>",unsafe_allow_html=True)

    # Verificar si los DataFrames están disponibles
        if "df_equipo_ensayo" in st.session_state and st.session_state.df_equipo_ensayo is not None:

            # Salto de línea
            st.markdown("<br>", unsafe_allow_html=True)

            #Información
            st.markdown("<p style='font-size: 18px;'><strong>Selecciona las variables y el tipo de gráfico a visualizar</strong></p>", unsafe_allow_html=True)

            variables_analizador_redes_diferido = st.multiselect('Analizador de redes',st.session_state.df_analizador_redes_ensayo.columns.tolist())
            variables_evaporador_04_diferido= st.multiselect('Evaporador 1',st.session_state.df_evaporador_04_ensayo.columns.tolist())
            variables_valvula_expansion_05_diferido = st.multiselect('Válvula expansion 1',st.session_state.df_valvula_expansion_05_ensayo.columns.tolist())
            variables_evaporador_06_diferido = st.multiselect('Evaporador 2',st.session_state.df_evaporador_06_ensayo.columns.tolist())
            variables_valvula_expansion_07_diferido = st.multiselect('Válvula expansion 2',st.session_state.df_valvula_expansion_07_ensayo.columns.tolist())
            variables_equipo_diferido = st.multiselect('Central transcrítica y gas-cooler',st.session_state.df_equipo_ensayo.columns.tolist())            
            indicadores_termodinamicos = st.multiselect('Indicadores termodinámicos',['COP','Diagramas P-H y T-S','Potencias del ciclo','Flujos másicos','Rendimientos del compresor','Caracterización de los evaporadores'])
            tipo_grafico_diferido = st.multiselect('Tipo de gráfico',['Scada','Gráfico de líneas','Tabla'])
            velocidad_reproduccion = st.slider("Velocidad de reproducción (segundos):",min_value=0.1,max_value=10.0,value=0.1,step=0.1)
            lista_variables_diferido=variables_analizador_redes_diferido+variables_evaporador_04_diferido+variables_valvula_expansion_05_diferido+variables_evaporador_06_diferido+variables_valvula_expansion_07_diferido+variables_equipo_diferido

            # Salto de línea
            st.markdown("<br>", unsafe_allow_html=True)

            # Botón para iniciar la actualización dinámica
            if st.button("Iniciar ensayo en diferido"):

                #Verificar si se seleccionaron variables
                if not tipo_grafico_diferido or (not lista_variables_diferido and not indicadores_termodinamicos):

                    st.warning("Selecciona al menos una variable y un tipo de gráfico")

                else:
                    # Salto de línea
                    st.markdown("<br>", unsafe_allow_html=True) 
       
                    representacion_grafico(indicadores_termodinamicos,velocidad_reproduccion,tipo_grafico_diferido,lista_variables_diferido,st.session_state.df_analizador_redes_ensayo,st.session_state.df_equipo_ensayo,st.session_state.df_evaporador_04_ensayo,st.session_state.df_valvula_expansion_05_ensayo,st.session_state.df_evaporador_06_ensayo,st.session_state.df_valvula_expansion_07_ensayo)            
                        
        else:
            st.warning("No se han cargado datos históricos")

    #elif menu_herramientas == 'Análisis Temporal':
#
    #    #Título
    #    st.markdown("<h2 style='text-align: center;'>Análisis Temporal</h2>",unsafe_allow_html=True)
#
    #    # Salto de línea
    #    st.markdown("<br>", unsafe_allow_html=True)
#
    #    menu_analisis_temporal = option_menu(
    #    menu_title=None,  
    #    options=["Gráfico de líneas", "Histograma","Mapas de calor"],
    #    default_index=0,
    #    orientation='horizontal',
    #    styles={
    #    "container": {"padding": "5px", "background-color": "#ffffff"},
    #    "icon": {"color": "orange", "font-size": "18px"},
    #    "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
    #    "nav-link-selected": {"background-color": "#03617E"}})
#
    #    # Salto de línea
    #    st.markdown("<br>", unsafe_allow_html=True)
#
    ## Verificar si los DataFrames están disponibles
    #    if "df_equipo_ensayo" in st.session_state and st.session_state.df_equipo_ensayo is not None:
#
    #        if menu_analisis_temporal=='Gráfico de líneas':
#
    #            #Información
    #            st.markdown("<p style='font-size: 18px;'><strong>Selecciona las variables</strong></p>", unsafe_allow_html=True)
#
    #            variables_analizador_redes_diferido = st.multiselect('Analizador de redes',st.session_state.df_analizador_redes_ensayo.columns.tolist())
    #            variables_evaporador_04_diferido= st.multiselect('Evaporador 1',st.session_state.df_evaporador_04_ensayo.columns.tolist())
    #            variables_valvula_expansion_05_diferido = st.multiselect('Válvula expansion 1',st.session_state.df_valvula_expansion_05_ensayo.columns.tolist())
    #            variables_evaporador_06_diferido = st.multiselect('Evaporador 2',st.session_state.df_evaporador_06_ensayo.columns.tolist())
    #            variables_valvula_expansion_07_diferido = st.multiselect('Válvula expansion 2',st.session_state.df_valvula_expansion_07_ensayo.columns.tolist())
    #            variables_equipo_diferido = st.multiselect('Central transcrítica y gas-cooler',st.session_state.df_equipo_ensayo.columns.tolist())            
    #            lista_variables_analisis=variables_analizador_redes_diferido+variables_evaporador_04_diferido+variables_valvula_expansion_05_diferido+variables_evaporador_06_diferido+variables_valvula_expansion_07_diferido+variables_equipo_diferido
#
    #        # Salto de línea
    #        st.markdown("<br>", unsafe_allow_html=True)
#
    #    else:
    #        st.warning("No se han cargado datos históricos")
#
#

    elif menu_herramientas == 'Estudio de Puntos Clave':

    # Verificar si los DataFrames están disponibles
        if "df_equipo_ensayo" in st.session_state and st.session_state.df_equipo_ensayo is not None:
            puntos = st.selectbox('Tipos de puntos',['','Cuasi-estacionarios','Sin restricciones'])

            if puntos=='Cuasi-estacionarios':
                metodo_busqueda = st.selectbox('Métodos de búsqueda',['','Últimos puntos activos del compresor','Variable comprendida en banda','Control combinado'])
                if metodo_busqueda=='Últimos puntos activos del compresor':
                    puntos_compresor=st.number_input('Últimos puntos activo',1,4,1)
                # Inicializar el estado de la aplicación para que no se active el selectbox de ensayos disponibles
                    if "puntos_encontrados" not in st.session_state:
                        st.session_state.puntos_encontrados = []
                    if st.button("Iniciar búsqueda"):

                        lista_estacionarios,puntos_encontrados=busqueda_puntos_compresor(puntos_compresor,st.session_state.df_analizador_redes_ensayo,st.session_state.df_equipo_ensayo,st.session_state.df_evaporador_04_ensayo,st.session_state.df_valvula_expansion_05_ensayo,st.session_state.df_evaporador_06_ensayo,st.session_state.df_valvula_expansion_07_ensayo)

                        #Verificar si la lista de ensayos está vacía
                        if not lista_estacionarios:
                            st.error('Cuasi-estacionarios no encontrados')
                        else:
                            # Mensaje de éxito o error
                            st.success("Búsqueda completada")

                            st.session_state.puntos_compresor=puntos_compresor
                            st.session_state.lista_estacionarios=lista_estacionarios
                            puntos_encontrados_copia=puntos_encontrados.copy()
                            puntos_encontrados=list()
                            for hora in puntos_encontrados_copia:
                                nuevo_instante=hora -timedelta(minutes=puntos_compresor-1)
                                puntos_encontrados.append((nuevo_instante,hora))
                            st.session_state.puntos_encontrados=puntos_encontrados

                    st.markdown("<br>", unsafe_allow_html=True)

                    if st.session_state.puntos_encontrados:

                        punto_compresor_seleccionado=st.selectbox('Cuasi-estacionarios disponibles',st.session_state.lista_estacionarios)
                        st.session_state.punto_compresor_seleccionado=punto_compresor_seleccionado

                        if st.button("Cálculos termodinámicos"):

                            calculos_termodinamicos(st.session_state.punto_compresor_seleccionado,st.session_state.lista_estacionarios,st.session_state.puntos_encontrados,st.session_state.df_analizador_redes_ensayo,st.session_state.df_equipo_ensayo,st.session_state.df_evaporador_04_ensayo,st.session_state.df_valvula_expansion_05_ensayo,st.session_state.df_evaporador_06_ensayo,st.session_state.df_valvula_expansion_07_ensayo)



                elif metodo_busqueda=='Variable comprendida en banda':

                    variables_disponibles=st.session_state.df_analizador_redes_ensayo.columns.tolist()+st.session_state.df_evaporador_04_ensayo.columns.tolist()+st.session_state.df_valvula_expansion_05_ensayo.columns.tolist()+st.session_state.df_evaporador_06_ensayo.columns.tolist()+st.session_state.df_valvula_expansion_07_ensayo.columns.tolist()+st.session_state.df_equipo_ensayo.columns.tolist()

                    variable_banda = st.selectbox('Variable',variables_disponibles,index=variables_disponibles.index("Temperatura camara (evaporador 1) (°C)"))
                    consigna=st.number_input('Consigna',-100.0,100.0,0.0)
                    banda_superior=st.number_input('Banda superior',-100.0,100.0,0.0)
                    banda_inferior=st.number_input('Banda inferior',-100.0,100.0,0.0)

                    if "puntos_encontrados_variable" not in st.session_state:
                        st.session_state.puntos_encontrados_variable = []
                    if st.button("Iniciar búsqueda"):

                        lista_estacionarios_variable,puntos_encontrados_variable=busqueda_puntos_variable(variable_banda,consigna,banda_superior,banda_inferior,st.session_state.df_analizador_redes_ensayo,st.session_state.df_equipo_ensayo,st.session_state.df_evaporador_04_ensayo,st.session_state.df_valvula_expansion_05_ensayo,st.session_state.df_evaporador_06_ensayo,st.session_state.df_valvula_expansion_07_ensayo)

                        #Verificar si la lista de ensayos está vacía
                        if not lista_estacionarios_variable:
                            st.error('Cuasi-estacionarios no encontrados')
                        else:
                        #    # Mensaje de éxito o error
                            st.success("Búsqueda completada")
#
                            st.session_state.lista_estacionarios_variable=lista_estacionarios_variable
                            st.session_state.puntos_encontrados_variable=puntos_encontrados_variable
                    st.markdown("<br>", unsafe_allow_html=True)

                    if st.session_state.puntos_encontrados_variable:
#
                        punto_variable_seleccionado=st.selectbox('Cuasi-estacionarios disponibles',st.session_state.lista_estacionarios_variable)
                        st.session_state.punto_variable_seleccionado=punto_variable_seleccionado
#
                        if st.button("Cálculos termodinámicos"):
#
                            calculos_termodinamicos(st.session_state.punto_variable_seleccionado,st.session_state.lista_estacionarios_variable,st.session_state.puntos_encontrados_variable,st.session_state.df_analizador_redes_ensayo,st.session_state.df_equipo_ensayo,st.session_state.df_evaporador_04_ensayo,st.session_state.df_valvula_expansion_05_ensayo,st.session_state.df_evaporador_06_ensayo,st.session_state.df_valvula_expansion_07_ensayo)

                elif metodo_busqueda=='Control combinado':
                    consigna_temperatura_camara=st.number_input('Consigna de la temperatura de cámara',-100.0,100.0,0.0)
                    banda_superior_temperatura_camara=st.number_input('Banda superior de la temperatura de cámara',-100.0,100.0,0.0)
                    banda_inferior_temperatura_camara=st.number_input('Banda inferior de la temperatura de cámara',-100.0,100.0,0.0)
                    consigna_temperatura=st.number_input('Consigna de la temperatura de evaporación',-100.0,100.0,0.0)
                    banda_superior_temperatura=st.number_input('Banda superior de la temperatura de evaporación',-100.0,100.0,0.0)
                    banda_inferior_temperatura=st.number_input('Banda inferior de la temperatura de evaporación',-100.0,100.0,0.0)
                    subrenfriamiento=st.number_input('Consigna de salto térmico en gas-cooler',0.0,50.0,0.0)
                    sobrecalentamiento=st.number_input('Consigna de salto térmico en evaporador',0.0,50.0,0.0)
                    apertura_valvula=st.number_input('Apertura de la válvula by-pass',0.0,100.0,0.0)

                    if "puntos_encontrados_control" not in st.session_state:
                        st.session_state.puntos_encontrados_control = []
                    if st.button("Iniciar búsqueda"):

                        lista_estacionarios_control,puntos_encontrados_control=busqueda_puntos_control(consigna_temperatura_camara,banda_superior_temperatura_camara,banda_inferior_temperatura_camara,consigna_temperatura,banda_superior_temperatura,banda_inferior_temperatura,subrenfriamiento,sobrecalentamiento,apertura_valvula,st.session_state.df_analizador_redes_ensayo,st.session_state.df_equipo_ensayo,st.session_state.df_evaporador_04_ensayo,st.session_state.df_valvula_expansion_05_ensayo,st.session_state.df_evaporador_06_ensayo,st.session_state.df_valvula_expansion_07_ensayo)

                        #Verificar si la lista de ensayos está vacía
                        if not lista_estacionarios_control:
                            st.error('Cuasi-estacionarios no encontrados')
                        else:
                        #    # Mensaje de éxito o error
                            st.success("Búsqueda completada")
#
                            st.session_state.lista_estacionarios_control=lista_estacionarios_control
                            st.session_state.puntos_encontrados_control=puntos_encontrados_control
                    st.markdown("<br>", unsafe_allow_html=True)

                    if st.session_state.puntos_encontrados_control:
#
                        punto_control_seleccionado=st.selectbox('Cuasi-estacionarios disponibles',st.session_state.lista_estacionarios_control)
                        st.session_state.punto_control_seleccionado=punto_control_seleccionado
#
                        if st.button("Cálculos termodinámicos"):
                            st.markdown("<br>", unsafe_allow_html=True)
                            calculos_termodinamicos(st.session_state.punto_control_seleccionado,st.session_state.lista_estacionarios_control,st.session_state.puntos_encontrados_control,st.session_state.df_analizador_redes_ensayo,st.session_state.df_equipo_ensayo,st.session_state.df_evaporador_04_ensayo,st.session_state.df_valvula_expansion_05_ensayo,st.session_state.df_evaporador_06_ensayo,st.session_state.df_valvula_expansion_07_ensayo)


            if puntos=='Sin restricciones':
                
                puntos_encontrados_sin_restricciones=list()
                lista_puntos_sin_restricciones=list()
                for i,hora in enumerate(st.session_state.df_equipo_ensayo.index):
                    puntos_encontrados_sin_restricciones.append((hora,hora))
                    lista_puntos_sin_restricciones.append(f'Punto {i+1} - {hora.strftime('%H:%M')}')

                st.session_state.puntos_encontrados_sin_restricciones=puntos_encontrados_sin_restricciones
                st.session_state.lista_puntos_sin_restricciones=lista_puntos_sin_restricciones
                punto_seleccionado_sin_restricciones=st.selectbox('Puntos disponibles',st.session_state.lista_puntos_sin_restricciones) 
                st.session_state.punto_seleccionado_sin_restricciones=punto_seleccionado_sin_restricciones

                if st.session_state.puntos_encontrados_sin_restricciones:
                    if st.button("Cálculos termodinámicos"):
                        st.markdown("<br>", unsafe_allow_html=True)
                        calculos_termodinamicos(st.session_state.punto_seleccionado_sin_restricciones,st.session_state.lista_puntos_sin_restricciones,st.session_state.puntos_encontrados_sin_restricciones,st.session_state.df_analizador_redes_ensayo,st.session_state.df_equipo_ensayo,st.session_state.df_evaporador_04_ensayo,st.session_state.df_valvula_expansion_05_ensayo,st.session_state.df_evaporador_06_ensayo,st.session_state.df_valvula_expansion_07_ensayo)


        else:
            st.warning("No se han cargado datos históricos")


    elif menu_herramientas == 'Modelo Termodinámico':
        temperatura_evaporacion=st.number_input('Temperatura de evaporación (°C)',-60.0,20.0,-20.0)
        salto_evaporador=st.number_input('Salto térmico en evaporador (K)',0.0,20.0,5.0)
        temperatura_ambiente=st.number_input('Temperatura ambiente (°C)',-10.0,40.0,25.0)
        salto_gascooler=st.number_input('Salto térmico en gas-cooler (K)',0.0,20.0,5.0)
        velocidad_compresor=st.number_input('Velocidad de giro del compresor (rev/s)',0.0,80.0,65.0)


        if st.button("Calcular modelo"):
            st.markdown("<br>", unsafe_allow_html=True)
            calculo_modelo(temperatura_evaporacion,salto_evaporador,temperatura_ambiente,salto_gascooler,velocidad_compresor)






#elif menu == "Contáctenos":
#    st.title("INFORMACIÓN DE CONTACTO")
#
#elif menu == "Soporte Técnico":
#    st.title("CHAT-BOT")




