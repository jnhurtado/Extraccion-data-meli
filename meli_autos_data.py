# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 20:37:49 2023

@author: jhurt
"""

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
from time import sleep
from datetime import datetime
import os

#Listas de variables a recorrer en el buscador del portal inmobiliario
regiones = ["rm-metropolitana"]

autos = {
    "toyota": ["yaris", "rav4", "corolla","4runner"],
    "nissan": ["versa", "qashqai", "kicks"],
    "hyundai": ["accent", "tucson", "santa-fe"],
    "kia": ["rio", "sportage", "seltos"],
    "mazda": ["3", "cx-30", "cx-5", "2"],
    "volkswagen": ["gol", "polo", "t-cross","golf","gti"],
    "ford": ["focus", "fiesta", "escape"],
    "subaru": ["impreza", "forester", "outback"],
    "suzuki": ["swift", "vitara", "s-cross", "baleno", "sport"],
    "peugeot": ["208", "3008", "508", "308", "2008"],
    "volvo": ["v40","v60","s40","s60","s80","s90"],
    "bmw": ["x1","x3","x5","116","118","320"],
    "skoda": ["rapid","fabia"],
    "Mini": ["cooper"]
}


anomin, anomax = 2015, 2023  #definir el rango de años a buscar
anos = [str(ano) for ano in range(anomin, anomax)]

#transmision = ["automático", "mecánico", "manual"] #, mecánico, manual]

#combustible = ["Diésel", "Bencina", "Gasolina"]



def obtener_texto(url):
   
    # Realizar una solicitud HTTP GET
    response = requests.get(url)
    
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Obtener el código fuente como texto
        html = response.text
    
    #else:
     #   print(f"Error al obtener el código fuente. Código de estado: {response.status_code}")
        
    return html
    
def obtener_resultados(html):
    # Crear un objeto BeautifulSoup
    soup1 = BeautifulSoup(html, 'html.parser')
    resultados = soup1.find('span', {'class': 'ui-search-search-result__quantity-results'})
    resultados = resultados.text if resultados else print("No se pudo obtener los resultados")
    
    return int(resultados.replace(" resultados", "").replace(".",""))
 
def obtener_data(html):
   # Listas para almacenar la información de cada departamento
   titulo_list = []
   dir_list = []
   kilometraje_list = []
   precio_list = []
   url_list = []

   # Separar el texto en distintos textos usando el patrón <div class="ui-search-item__title-label-grid">
   autos_elements = html.split('</path></svg></span></button></div></section>')[1:]#'</path></svg></span></button></div></section>')[1:]#'<div class="ui-search-item__title-label-grid">')[1:]


   # Iterar sobre los elementos de los departamentos
   for autos_element in autos_elements:

       # Crear un objeto BeautifulSoup
       soup = BeautifulSoup(autos_element, 'html.parser')

       # Inicializar las variables con NaN para este departamento
       titulo = np.nan
       dire = np.nan
       kilometraje = np.nan
       precio= np.nan
       url = np.nan

       # Encontrar el elemento que contiene los metros útiles
       km_element = soup.find('li', class_='ui-search-card-attributes__attribute', string=lambda text: " Km" in text)
       if km_element:
           kilometraje = km_element.text

       # Encontrar el elemento <div> que contiene el título
       h2_element = soup.find('p', class_= 'ui-search-item__location')
       if h2_element:
           dire = h2_element.text

       # Obtener el valor de UF (Unidad de Fomento)
       precio_element = soup.find('span', {'class': 'andes-money-amount__fraction'})
       precio = precio_element.text if precio_element else None

       # Encontrar todas las etiquetas 'a' con la clase 'ui-search-result__image'
       enlace = soup.find('a', class_='ui-search-item__group__element')
       url = enlace.get('href') if enlace else None

       # Encontrar todas las etiquetas 'a' con la clase 'ui-search-result__image'
       titulo = enlace.get('title') if enlace else None


       # Agregar la información de este departamento a las listas

       titulo_list.append(titulo)
       dir_list.append(dire)
       kilometraje_list.append(kilometraje)
       precio_list.append(precio)
       url_list.append(url)


   # Crear un DataFrame de Pandas con la información de todos los departamentos
   data = {
       "Titulo": titulo_list,
       "Direccion": dir_list,
       "Kilometraje": kilometraje_list,
       "Precio": precio_list,
       "URL": url_list#[:-1]
   }

   df = pd.DataFrame(data)


   df["Precio"] = df["Precio"].str.replace(".","", regex=True).astype(float)


   return df

# Crear un objeto tqdm para mostrar la barra de progreso
criterios = 0
ini_marca, ini_modelo = "",""
for marca, modelos in autos.items():
    for modelo in modelos:
        criterios += 1
        ini_marca, ini_modelo = marca, modelo
        
criterios = criterios*len(anos)*len(regiones)

# Crea una barra de progreso para el proceso global.
progress_bar_total = tqdm(total=criterios, desc="Iterando por los criterios de búsqueda")  

# Inicializa una variable para contar errores.
errores = 0  

if os.path.exists("Data_meli_autos.csv"):  # Comprueba si ya existe un archivo CSV con datos antiguos.
    data_antigua = pd.read_csv("Data_meli_autos.csv")  # Lee los datos antiguos desde el archivo CSV.

else:
    # Si no existe un archivo CSV, construye una URL específica y obtén datos iniciales.
    url_especifica = f"https://autos.mercadolibre.cl/{ini_marca}/{regiones[0]}/{anos[0]}/{ini_modelo}"
    data_antigua = obtener_data(obtener_texto(url_especifica))

for marca, modelos in autos.items():
    for modelo in modelos:
        for region in regiones:
            for ano in anos:

                    
                        # Pausamos para evitar request demasiado seguidos.
                        sleep(np.random.randint(1,20)/10)           
                        buscar = 1            
                        progress_bar_total.update(1)
                        url_especifica = f"https://autos.mercadolibre.cl/{marca}/{region}/{ano}/{modelo}"
                        
                        try:
                            resultados = obtener_resultados(obtener_texto(url_especifica ))
                        except:
                            resultados = 0
                        
                        if resultados > 2000:
                            print(f"La {marca}, {modelo}, {region}, {ano} debe ser segmentada, debido a que supera el límite de 42 páginas del portal")
                            resultados = 2001
                        
                        # Crear un objeto tqdm para mostrar la barra de progreso
                        #progress_bar = tqdm(total=resultados, desc=f"Extrayendo {marca}, {modelo}, {region}, {ano}, {tipo}")
                        if resultados > 0:
                            
                            data = obtener_data(obtener_texto(url_especifica))
                            
                            while buscar <= resultados and resultados > 48:
                                
                                # Pausamos para evitar request demasiado seguidos.
                                sleep(np.random.randint(1,5)/10)
                                
                                buscar += 48
                                
                                url_especifica = f"https://autos.mercadolibre.cl/{marca}/{region}/{ano}/{modelo}/_Desde_{buscar}_NoIndex_True"
                                
                                saltar = False
                                
                                try: 
                                    data_hoja = obtener_data(obtener_texto(url_especifica))
                                    
                                except Exception as e:
                                    #print(f"Error al procesar {url_especifica}: {e}") 
                                    errores +=1
                                    saltar = True
                                    
                                if not saltar:
                                    data = pd.concat([data,data_hoja])
            
                                #progress_bar.update(48)
                                
                            # Eliminamos traslapes
                            data = data.drop_duplicates()
                            
                            # Agregamos columnas
                            

                            data["Region"]= region
                            data["Ano"] = ano
                            data["Modelo"] = modelo  
                            data["Marca"]= marca
              
                            
                            data = data.dropna(subset=['Precio'])
                            
                            # Agregar la data nueva
                            data_antigua = pd.concat([data_antigua,data])
                            
                            # Eliminamos traslapes
                            data_antigua = data_antigua.drop_duplicates()
                            
                            # Reordeamos las columnas
                            nuevo_orden_columnas = ["Marca", "Modelo", "Ano", "Precio", "Kilometraje", "Titulo", "URL"]
                            data_antigua = data_antigua[nuevo_orden_columnas]

                            data_antigua = data_antigua.dropna(subset=['Ano'])

                            # Eliminamos traslapes
                            data_antigua = data_antigua.drop_duplicates()

                            data_antigua.replace("ñ","n", regex=True).to_csv("Data_meli_autos.csv",index=False)
 
            
print("Errores: ", errores)



#data_antigua = data_antigua.drop(columns=["Titulo"])  #lo votamos por ahora q no resulta

#data_antigua = data_antigua.drop(columns=["Direccion"]) #lo votamos por ahora q no resulta

# Reordeamos las columnas
nuevo_orden_columnas = ["Marca", "Modelo", "Ano", "Precio", "Kilometraje","Titulo", "URL"]
data_antigua = data_antigua[nuevo_orden_columnas]

data_antigua = data_antigua.dropna(subset=['Ano'])

data_antigua["Fecha extraccion"] = "{}/{}/{}".format(datetime.now().day, datetime.now().month, datetime.now().year)

# Eliminamos traslapes
data_antigua = data_antigua.drop_duplicates()

data_antigua.replace("ñ","n", regex=True).to_csv("Data_meli_autos.csv",index=False)



