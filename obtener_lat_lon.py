# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 14:29:27 2023

@author: jhurt
"""
from geopy.geocoders import Nominatim
from tqdm import tqdm
import pandas as pd



def obtener_latitud_longitud_osm(direccion):
    geolocalizador = Nominatim(user_agent="mi_app")  # Debes definir un nombre de usuario para el user_agent
    try:
        location = geolocalizador.geocode(direccion)
        if location:
            print(f"La dirección '{direccion}' tiene una latitud de {location.latitude} y una longitud de {location.longitude}.")
            return location.latitude, location.longitude
        else:
            print("No se pudo encontrar la ubicación.")
            return None, None
    except Exception as e:
        print("Error:", e)
        return None, None

# Ingresa la dirección que deseas buscar
direccion = "Hernando de Aguirre 1958, Providencia, Chile"

# Llamada a la función para obtener latitud y longitud
latitud, longitud = obtener_latitud_longitud_osm(direccion)

# Lee los datos antiguos desde el archivo CSV.
data = pd.read_csv("Data_portal_inmobiliario.csv")  

Data_filtrada = data[data["Tipo inmueble"] == "departamento"][data['Tipo oferta'] == "arriendo"][data["Comuna"]=="providencia-metropolitana"].dropna()

# Imprimir los resultados
progress_bar = tqdm(total=len(Data_filtrada), desc="Iterando por cada dirección")  # Crea una barra de progreso para el proceso global.
LAT = []
LON = []
for fila in range(len(Data_filtrada)):
    direccion = str(Data_filtrada["Direccion"].values[fila]).replace("...", ",Providencia, Chile")
    lat, lon = obtener_latitud_longitud_osm(direccion)
    LAT.append(lat)
    LON.append(lon)
    progress_bar.update(1)