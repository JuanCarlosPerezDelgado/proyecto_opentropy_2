from datetime import datetime         
import pandas as pd
import matplotlib.pyplot as plt     
import numpy as np

def busqueda(instalacion,fecha_inicio,fecha_fin,duracion_minutos):

    #Comprobación de instalación
    if instalacion=='Equipo para cámaras de refrigeración y congelación de CO2 transcrítico (Escuela de Ingeniería Industriales - Universidad de Málaga)':

        #EXTRACCIÓN DE DATOS
        df_analizador_redes=pd.read_excel('ensayos/analizadorderedes.xlsx',index_col=0,parse_dates=True)
        df_equipo=pd.read_excel('ensayos/equipo.xlsx',index_col=0,parse_dates=True)
        df_evaporador_04=pd.read_excel('ensayos/evaporador04.xlsx',index_col=0,parse_dates=True)
        df_valvula_expansion_05=pd.read_excel('ensayos/valvulaexpansion05.xlsx',index_col=0,parse_dates=True)
        df_evaporador_06=pd.read_excel('ensayos/evaporador06.xlsx',index_col=0,parse_dates=True)
        df_valvula_expansion_07=pd.read_excel('ensayos/valvulaexpansion07.xlsx',index_col=0,parse_dates=True)

        #SELECCIÓN Y FILTRADO: SELECCIONAR ENSAYOS VÁLIDOS

        #Configuración del intervalo de búsqueda de los ensayos
        dia_inicio=str(fecha_inicio.day)
        mes_inicio=str(fecha_inicio.month)
        año_inicio=str(fecha_inicio.year)
        dia_fin=str(fecha_fin.day)
        mes_fin=str(fecha_fin.month)
        año_fin=str(fecha_fin.year)
        duracion=int(duracion_minutos)
        fecha_texto_inicio='{d}/{m}/{a} 00:00:00'
        fecha_texto_inicio=fecha_texto_inicio.format(d=dia_inicio,m=mes_inicio,a=año_inicio)
        fecha_texto_fin='{d}/{m}/{a} 23:59:00'
        fecha_texto_fin=fecha_texto_fin.format(d=dia_fin,m=mes_fin,a=año_fin)
        formato='%d/%m/%Y %H:%M:%S'
        fecha_inicio=datetime.strptime(fecha_texto_inicio,formato)
        fecha_fin=datetime.strptime(fecha_texto_fin,formato)

        #Búsqueda de ensayos
        intervalos_ensayos=list()
        contador=0
        inicio=None
        indice_anterior=None
        for i, (indice,valor) in enumerate(df_evaporador_04.loc[fecha_inicio:fecha_fin,'Estado dispositivo (evaporador 1) (on/off)'].items()):
            if valor==1:
                if contador==0:
                    inicio=indice
                contador +=1
                indice_anterior=indice
            else:
                if contador >= duracion:
                    intervalos_ensayos.append((inicio,indice_anterior))
                contador=0
        if contador >= duracion:
            intervalos_ensayos.append((inicio, df_evaporador_04.index[-1]))

        lista_ensayos=list()
        for i, (inicio, fin) in enumerate(intervalos_ensayos):
            duracion=((fin - inicio).total_seconds() / 60)+1
            lista_ensayos.append(f'Ensayo {i+1} - Desde {inicio} hasta {fin} - Duración {duracion} min')


    #Ensayos encontrados
    return lista_ensayos,intervalos_ensayos,df_analizador_redes,df_equipo,df_evaporador_04,df_valvula_expansion_05,df_evaporador_06,df_valvula_expansion_07
        
def ensayo(ensayo_seleccionado,lista_ensayos,intervalos_ensayos,df_analizador_redes,df_equipo,df_evaporador_04,df_valvula_expansion_05,df_evaporador_06,df_valvula_expansion_07):

    #Intervalo de tiempo del ensayo seleccionado
    info_ensayo=lista_ensayos.index(ensayo_seleccionado)
    inicio,fin=intervalos_ensayos[info_ensayo]

    #PREPROCESADO

    #Generación de subdataframe en función del ensayo elegido
    df_analizador_redes_ensayo=df_analizador_redes.loc[inicio:fin,:]
    df_equipo_ensayo=df_equipo.loc[inicio:fin,:]
    df_evaporador_04_ensayo=df_evaporador_04.loc[inicio:fin,:]
    df_valvula_expansion_05_ensayo=df_valvula_expansion_05.loc[inicio:fin,:]
    df_evaporador_06_ensayo=df_evaporador_06.loc[inicio:fin,:]
    df_valvula_expansion_07_ensayo=df_valvula_expansion_07.loc[inicio:fin,:]

    #Establecer el índice correcto
    df_analizador_redes_ensayo.index=df_analizador_redes_ensayo.index.floor('min')
    inicio_df_analizador_redes_ensayo=df_analizador_redes_ensayo.index[0]
    fin_df_analizador_redes_ensayo=df_analizador_redes_ensayo.index[-1]
    indice_nuevo_df_analizador_redes_ensayo=pd.date_range(start=inicio_df_analizador_redes_ensayo,end=fin_df_analizador_redes_ensayo,freq='min')
    df_analizador_redes_ensayo=df_analizador_redes_ensayo.reindex(indice_nuevo_df_analizador_redes_ensayo)

    df_equipo_ensayo.index=df_equipo_ensayo.index.floor('min')
    inicio_df_equipo_ensayo=df_equipo_ensayo.index[0]
    fin_df_equipo_ensayo=df_equipo_ensayo.index[-1]
    indice_nuevo_df_equipo_ensayo=pd.date_range(start=inicio_df_equipo_ensayo,end=fin_df_equipo_ensayo,freq='min')
    df_equipo_ensayo=df_equipo_ensayo.reindex(indice_nuevo_df_equipo_ensayo)

    df_evaporador_04_ensayo.index=df_evaporador_04_ensayo.index.floor('min')
    inicio_df_evaporador_04_ensayo=df_evaporador_04_ensayo.index[0]
    fin_df_evaporador_04_ensayo=df_evaporador_04_ensayo.index[-1]
    indice_nuevo_df_evaporador_04_ensayo=pd.date_range(start=inicio_df_evaporador_04_ensayo,end=fin_df_evaporador_04_ensayo,freq='min')
    df_evaporador_04_ensayo=df_evaporador_04_ensayo.reindex(indice_nuevo_df_evaporador_04_ensayo)

    df_valvula_expansion_05_ensayo.index=df_valvula_expansion_05_ensayo.index.floor('min')
    inicio_df_valvula_expansion_05_ensayo=df_valvula_expansion_05_ensayo.index[0]
    fin_df_valvula_expansion_05_ensayo=df_valvula_expansion_05_ensayo.index[-1]
    indice_nuevo_df_valvula_expansion_05_ensayo=pd.date_range(start=inicio_df_valvula_expansion_05_ensayo,end=fin_df_valvula_expansion_05_ensayo,freq='min')
    df_valvula_expansion_05_ensayo=df_valvula_expansion_05_ensayo.reindex(indice_nuevo_df_valvula_expansion_05_ensayo)

    df_evaporador_06_ensayo.index=df_evaporador_06_ensayo.index.floor('min')
    inicio_df_evaporador_06_ensayo=df_evaporador_06_ensayo.index[0]
    fin_df_evaporador_06_ensayo=df_evaporador_06_ensayo.index[-1]
    indice_nuevo_df_evaporador_06_ensayo=pd.date_range(start=inicio_df_evaporador_06_ensayo,end=fin_df_evaporador_06_ensayo,freq='min')
    df_evaporador_06_ensayo=df_evaporador_06_ensayo.reindex(indice_nuevo_df_evaporador_06_ensayo)

    df_valvula_expansion_07_ensayo.index=df_valvula_expansion_07_ensayo.index.floor('min')
    inicio_df_valvula_expansion_07_ensayo=df_valvula_expansion_07_ensayo.index[0]
    fin_df_valvula_expansion_07_ensayo=df_valvula_expansion_07_ensayo.index[-1]
    indice_nuevo_df_valvula_expansion_07_ensayo=pd.date_range(start=inicio_df_valvula_expansion_07_ensayo,end=fin_df_valvula_expansion_07_ensayo,freq='min')
    df_valvula_expansion_07_ensayo=df_valvula_expansion_07_ensayo.reindex(indice_nuevo_df_valvula_expansion_07_ensayo)

    #Eliminación de la columna a la que le faltan todos los datos
    df_analizador_redes_ensayo=df_analizador_redes_ensayo.dropna(axis='columns',how='all')
    df_equipo_ensayo=df_equipo_ensayo.dropna(axis='columns',how='all')
    df_evaporador_04_ensayo=df_evaporador_04_ensayo.dropna(axis='columns',how='all')
    df_valvula_expansion_05_ensayo=df_valvula_expansion_05_ensayo.dropna(axis='columns',how='all')
    df_evaporador_06_ensayo=df_evaporador_06_ensayo.dropna(axis='columns',how='all')
    df_valvula_expansion_07_ensayo=df_valvula_expansion_07_ensayo.dropna(axis='columns',how='all')

    #Rellenado de datos omitidos
    df_analizador_redes_ensayo=df_analizador_redes_ensayo.interpolate()
    df_analizador_redes_ensayo=df_analizador_redes_ensayo.bfill()
    df_analizador_redes_ensayo=df_analizador_redes_ensayo.round(2)

    df_equipo_ensayo=df_equipo_ensayo.interpolate()
    df_equipo_ensayo=df_equipo_ensayo.bfill()
    df_equipo_ensayo=df_equipo_ensayo.round(2)

    df_evaporador_04_ensayo=df_evaporador_04_ensayo.interpolate()
    df_evaporador_04_ensayo=df_evaporador_04_ensayo.bfill()
    df_evaporador_04_ensayo=df_evaporador_04_ensayo.round(2)

    df_valvula_expansion_05_ensayo=df_valvula_expansion_05_ensayo.interpolate()
    df_valvula_expansion_05_ensayo=df_valvula_expansion_05_ensayo.bfill()
    df_valvula_expansion_05_ensayo=df_valvula_expansion_05_ensayo.round(2)

    df_evaporador_06_ensayo=df_evaporador_06_ensayo.interpolate()
    df_evaporador_06_ensayo=df_evaporador_06_ensayo.bfill()
    df_evaporador_06_ensayo=df_evaporador_06_ensayo.round(2)

    df_valvula_expansion_07_ensayo=df_valvula_expansion_07_ensayo.interpolate()
    df_valvula_expansion_07_ensayo=df_valvula_expansion_07_ensayo.bfill()
    df_valvula_expansion_07_ensayo=df_valvula_expansion_07_ensayo.round(2)


    #Ensayo seleccionado
    return df_analizador_redes_ensayo,df_equipo_ensayo,df_evaporador_04_ensayo,df_valvula_expansion_05_ensayo,df_evaporador_06_ensayo,df_valvula_expansion_07_ensayo