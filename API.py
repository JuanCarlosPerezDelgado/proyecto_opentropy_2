import requests # Peticiones HTTP
import numpy as np # Vectores, matrices, etc.
import pandas as pd # Analisis de datos
from datetime import datetime, timedelta

#Definición de la URL de la API
URL = "https://kicloud.kiconex.com/api/v1"

#Función que devuelve el HEADER de las peticiones.
def request_headers(token: str):
  return {
      'Content-Type':'application/json',
      'Authorization': f'Basic {token}'
  }
#Funciones para realizar autenticación (y 2FA en caso de que esté activado en el perfil de la plataforma).
def request_tfa(token: str, code: str):
    url_login = f"{URL}/login/tfa"

    payload = {
        'token': token,
        'tfa': code,
    }

    response = requests.post(
        url_login,
        headers=request_headers(token),
        json=payload)

    if response.status_code != 200:
        print(f"API exception: {response}")
        return False

    res = response.json()
    if not res['is_active'] and res['user_tfa']:
        print("TFA not valid.")
        return False

    print("TFA code accepted")

    return True

def request_login(username: str, password: str):
    url_login = f"{URL}/login"

    headers = {
        'Conten-Type': 'application/json'
    }

    payload = {
        'name': username,
        'password': password
    }

    response = requests.post(
        url_login,
        headers=headers,
        json=payload)

    if response.status_code != 200:
        print(f"API exception: {response}")
        return ""

    res = response.json()

    if not res['is_active'] and res['user_tfa']:
        print("TFA required (5 attemps)...")
        tfa_op = False
        for i in range(5):
          tfa_code = input("Enter TFA code: ")
          tfa_op = request_tfa(res['token'], tfa_code)
          if tfa_op:
            break

        if not tfa_op:
          print("TFA code not accepted")
          return ""

    print("Log in successful!")
    return res['token']

#Petición de histórico de datos y post-procesamiento para transformar la respuesta a DataFrame para hacer análisis de datos (esta petición se hace a la base de datos del servidor)
def request_charts_body(device_uuid, control_uuid, entities, from_str, until_str, interval):
  series_list = []
  for entity in entities:
    series_list.append(
            {
              "device": { "uuid": device_uuid },
              "control": {"uuid": control_uuid },
              "parameter":{ "id": entity["id"]},
            }
    )

  return {
        "parameters": {
            "format": "raw",
            "from": from_str,
            "until": until_str,
            "interval": f"{interval}",
            "sections": [{"series": series_list}]
        }
      }

def make_charts_request(token, device_uuid, control_uuid, entities, from_str, until_str, interval):
  response = requests.post(
      f"{URL}/charts",
      headers=request_headers(token),
      json=request_charts_body(
            device_uuid,
            control_uuid,
            entities,
            from_str,
            until_str,
            interval
          )
      )
  if response.status_code != 200:
      print(f"Error con mykiconex: {response.status_code}")
      return {}

  return response.json()

def process_charts_response(device_uuid, control_uuid, entities, response_dict):
  df = pd.DataFrame()

  for entity in entities:
    df_tmp = pd.DataFrame(response_dict["data"][0][f"{device_uuid}.{control_uuid}.{entity['id']}"]['values']).drop(columns=["parameter", "serie_name", "serie_unit"])
    if df.empty:
      df = df_tmp
    else:
      df = pd.merge(df, df_tmp, on='timestamp')

    df.rename(columns={f"data{entity['id']}": entity["name"]}, inplace=True)

  df["timestamp"] = pd.to_datetime(df["timestamp"], format='%Y-%m-%d %H:%M:%S %z')
  df.set_index("timestamp", inplace=True)

  return df

#Petición para obtener datos en tiempo real
def make_status_request(token, device_uuid, control_uuid, entity_id):
  response = requests.get(f"{URL}/devices/{device_uuid}/controls/{control_uuid}/parameters/{entity_id}", headers=request_headers(token))
  if response.status_code != 200:
      print(f"Error con mykiconex: {response.status_code}")
      return {}

  return response.json()

def process_status_response(response_dict):
  return {"value": response_dict["status"]["value"], "timestamp": response_dict["status"]["last_change"]}