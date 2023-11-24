# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 21:47:33 2023

@author: jhurt
"""

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
from time import sleep
import os
from datetime import datetime



def obtener_texto(url):
   
    # Realizar una solicitud HTTP GET
    response = requests.get(url)
    
    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        # Obtener el código fuente como texto
        html = response.text
    
    else:
        print(f"Error al obtener el código fuente. Código de estado: {response.status_code}")
        
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
    metros_utiles_list = []
    dormitorios_list = []
    banos_list = []
    uf_list = []
    valor_uf_list = []
    encabezado_list = []
    url_list = [np.nan]
    
    # Separar el texto en distintos textos usando el patrón <div class="ui-search-item__title-label-grid">
    departamento_elements = html.split('class="ui-search-result__content-wrapper ui-search-link"')[1:]#'</path></svg></span></button></div></section>')[1:]#'<div class="ui-search-item__title-label-grid">')[1:]

    
    # Iterar sobre los elementos de los departamentos
    for departamento_element in departamento_elements:
        
        # Crear un objeto BeautifulSoup
        soup = BeautifulSoup(departamento_element, 'html.parser')
        
        # Inicializar las variables con NaN para este departamento
        titulo = np.nan
        metros_utiles = np.nan
        dormitorios = "1 dormitorio"
        banos = "1 baño"
        uf = np.nan
        valor_uf = np.nan
        url = np.nan
        encabezado = np.nan
        
        
        # Encontrar el elemento que contiene los metros útiles
        metros_utiles_element = soup.find('li', class_='ui-search-card-attributes__attribute', string=lambda text: "m² útiles" in text)
        if metros_utiles_element:
            metros_utiles = metros_utiles_element.text
            
        # Encontrar el elemento que contiene los dormitorios
        dormitorios_element = soup.find('li', class_='ui-search-card-attributes__attribute', string=lambda text: "dormitorios" in text)
        if dormitorios_element:
            dormitorios = dormitorios_element.text
            
        # Encontrar el elemento que contiene los baños
        banos_element = soup.find('li', class_='ui-search-card-attributes__attribute', string=lambda text: "baños" in text)
        if banos_element:
            banos = banos_element.text
            
        # Encontrar el elemento <div> que contiene el título
        h2_element = soup.find('p', class_= 'ui-search-item__location-label')
        if h2_element:
            titulo = h2_element.text

        # Obtener el valor de UF (Unidad de Fomento)
        uf_element = soup.find('span', {'class': 'andes-money-amount__currency-symbol'})
        uf = uf_element.text if uf_element else None
        if uf_element:
            uf = uf_element.text
            
        # Obtener el valor de UF (Unidad de Fomento)
        valor_uf_element = soup.find('span', {'class': 'andes-money-amount__fraction'})
        valor_uf = valor_uf_element.text if valor_uf_element else None
        
        # Encontrar todas las etiquetas 'a' con la clase 'ui-search-result__image'
        enlace = soup.find('a', class_='ui-search-result__image')
        url = enlace.get('href') if enlace else None
        encabezado = enlace.get("title") if enlace else None

        # Agregar la información de este departamento a las listas
        titulo_list.append(titulo)
        encabezado_list.append(encabezado)
        metros_utiles_list.append(metros_utiles)
        dormitorios_list.append(dormitorios)
        banos_list.append(banos)
        uf_list.append(uf)
        valor_uf_list.append(valor_uf)
        url_list.append(url)
    
    # Crear un DataFrame de Pandas con la información de todos los departamentos
    data = {
        "Direccion": titulo_list,
        "Titulo": encabezado_list,
        "Metros Utiles": metros_utiles_list,
        "Dormitorios": dormitorios_list,
        "Baños": banos_list,
        "Moneda": uf_list,
        "Valor": valor_uf_list,
        "URL": url_list[:-1]
    }
    
    df = pd.DataFrame(data)
    
    
    df["Valor"] = df["Valor"].str.replace(".","", regex=True).astype(float)
    df["Valor pesos"] = df[df["Moneda"]=="UF"]["Valor"]*uf_pesos
    df["Valor pesos"] = df["Valor pesos"].fillna(0)
    df["Valor pesos2"] = df[df["Moneda"]!="UF"]["Valor"]
    df["Valor pesos2"] = df["Valor pesos2"].fillna(0)
    df["Valor pesos"] += df["Valor pesos2"]
    df.drop(columns=["Valor pesos2"]) 
    
    # Remover la palabra " dormitorios" y cualquier carácter no numérico
    try:
        df["Dormitorios"] = df["Dormitorios"].str.replace("[^\d.]", "", regex=True)
    except:
        df["Dormitorios"] = "9999"
    
    # Convertir la columna "Dormitorios" a tipo float
    try:
        df["Dormitorios"] = df["Dormitorios"].astype(float)
    except:
        df["Dormitorios"] = 9999
        
    # Calcular el valor dividido por la cantidad de dormitorios y crear una nueva columna "Valor por Dormitorio"
    df["Valor por Dormitorio"] = df["Valor pesos"] / df["Dormitorios"]
    
    # Remover la palabra " m² útiles" y cualquier carácter no numérico
    try :
        df["Metros Utiles"] = df["Metros Utiles"].str.replace("[^\d.]", "", regex=True)
    except:
        df["Metros Utiles"] = "9999"
        
    # Convertir la columna "Metros Útiles" a tipo float
    try :
        df["Metros Utiles"] = df["Metros Utiles"].astype(float)
    except:
        df["Metros Utiles"] = 9999
        
    # Calcular el valor dividido por los metros útiles y crear una nueva columna "Valor por Metro Cuadrado Útil"
    df["Valor/m2"] = df["Valor pesos"]/ df["Metros Utiles"]
    
    df = df.drop(columns=["Valor pesos2"])
    
    return df
#df.replace("ñ","n", regex=True).to_csv("hola.csv",index=False)


#Listas de variables a recorrer en el buscador del portal inmobiliario
regiones_de_chile = {
        "metropolitana" : [
            "alhue",
            "buin",
            "calera-de-tango",
            "cerrillos",
            "cerro-navia",
            "colina",
            "conchali",
            "curacavi",
            "el-bosque",
            "el-monte",
            "estacion-central",
            "huechuraba",
            "independencia",
            "isla-de-maipo",
            "la-cisterna",
            "la-florida",
            "la-granja",
            "la-pintana",
            "la-reina",
            "lampa",
            "lo-barnechea",
            "lo-espejo",
            "lo-prado",
            "macul",
            "maipu",
            "maria-pinto",
            "melipilla",
            "ñuñoa",
            "padre-hurtado",
            "paine",
            "pedro-aguirre-cerda",
            "peñaflor",
            "peñalolen",
            "pirque",
            "providencia",
            "pudahuel",
            "puente-alto",
            "quilicura",
            "quinta-normal",
            "recoleta",
            "renca",
            "san-bernardo",
            "san-joaquin",
            "san-jose-de-maipo",
            "san-miguel",
            "san-pedro",
            "san-ramon",
            "santiago",
            "talagante",
            "tiltil",
            "vitacura",
            "Alto-las-condes-santiago",
            "Barrio-El-Golf-las-condes-santiago",
            "Centro-Financiero-las-condes-santiago",
            "Colon-Oriente---Vital-Apoquindo-las-condes-santiago",
            "El-Remanso-las-condes-santiago",
            "Estoril-las-condes-santiago",
            "Los-Dominicos-las-condes-santiago",
            "Mall-Sport-las-condes-santiago",
            "Metro-Escuela-Militar-las-condes-santiago",
            "Metro-Hernando-de-Magallanes-las-condes-santiago",
            "metro-manquehue-apumanque-las-condes-santiago",
            "Nueva-las-condes-santiago",
            "Parque-Arauco-las-condes-santiago",
            "Parque-Padre-Alberto-Hurtado-las-condes-santiago",
            "Quinchamali-las-condes-santiago",
            "Rotonda-Atenas-las-condes-santiago",
            "San-Carlos-de-Apoquindo-las-condes-santiago",
            "San-Damian-las-condes-santiago",
            "Sebastian-Elcano-las-condes-santiago",
            "Vaticano-las-condes-santiago"
        ],
        "arica-y-parinacota":[
            "arica",
            "camarones",
            "general-lagos",
            "putre"
        ],
        "tarapaca":[
            "alto-hospicio",
            "iquique",
            "pozo-almonte"
        ],
        "antofagasta":[
            "antofagasta",
            "calama",
            "maria-elena",
            "mejillones",
            "ollague",
            "san-pedro-de-atacama",
            "sierra-gorda",
            "taltal",
            "tocopilla"
        ],
        "atacama":[
            "caldera",
            "chanaral",
            "copiapo",
            "diego-de-almagro",
            "freirina",
            "huasco",
            "tierra-amarilla",
            "vallenar"
        ],
        "coquimbo":[
            "andacollo",
            "coquimbo",
            "la-higuera",
            "la-serena",
            "paiguano",
            "punitaqui",
            "sallipud",
            "vicuna"
        ],
        "valparaiso":[
            "algarrobo",
            "cabildo",
            "calera",
            "calle-larga",
            "cartagena",
            "casablanca",
            "catemu",
            "concon",
            "el-quisco",
            "el-tabo",
            "hijuelas",
            "isla-de-pascua",
            "juan-fernandez",
            "la-cruz",
            "la-ligua",
            "limache",
            "llay-llay",
            "los-andes",
            "nogales",
            "olmue",
            "panquehue",
            "papudo",
            "petorca",
            "puchuncavi",
            "putaendo",
            "quilpue",
            "quintero",
            "san-antonio",
            "san-esteban",
            "san-felipe",
            "santa-maria",
            "santo-domingo",
            "valparaiso",
            "villa-alemana",
            "viña-del-mar"
        ],
        "ohiggins":[
            "chimbarongo",
            "codegua",
            "coinco",
            "coltauco",
            "doñihue",
            "graneros",
            "la-estrella",
            "las-cabras",
            "litueche",
            "lo-miranda",
            "machali",
            "malloa",
            "marchihue",
            "mostazal",
            "nageles",
            "olivar",
            "palmilla",
            "palmilla",
            "peumo",
            "pichidegua",
            "pichilemu",
            "placilla",
            "pumanque",
            "querihue",
            "rancagua",
            "rengo",
            "requinoa",
            "san-fernando",
            "san-francisco-de-mostazal",
            "san-vicente-de-tagua-tagua",
            "santa-cruz"
        ],
        "maule":[
            "cauquenes",
            "chanco",
            "colbun",
            "constitucion",
            "curepto",
            "curico",
            "empedrado",
            "hualañe",
            "linares",
            "longavi",
            "maule",
            "molina",
            "parral",
            "pelarco",
            "pelluhue",
            "pencahue",
            "rauco",
            "retiro",
            "romeral",
            "rio-claro",
            "sagrada-familia",
            "san-clemente",
            "san-javier",
            "san-rafael",
            "talca",
            "teno",
            "villa-alegre",
            "yumbel",
            "ñiquen"
        ],
        "biobio":[
            "alto-biobio",
            "antuco",
            "arauco",
            "cabrero",
            "cañete",
            "chiguayante",
            "concepcion",
            "contulmo",
            "coronel",
            "curanilahue",
            "huaquen",
            "lebu",
            "los-alamos",
            "los-angeles",
            "lota",
            "mulchen",
            "nacimiento",
            "negrete",
            "penco",
            "quilleco",
            "quilpue",
            "san-pedro-de-la-paz",
            "santa-barbara",
            "santa-juana",
            "talcahuano",
            "tirua",
            "tome",
            "yumbel",
            "lota",
            "san-rosendo",
            "tucapel"
        ],
            "araucania":[
            "angol",
            "carahue",
            "cholchol",
            "collipulli",
            "curacautin",
            "curarrehue",
            "ercilla",
            "freire",
            "galvarino",
            "gorbea",
            "lautaro",
            "loncoche",
            "lonquimay",
            "los-sauzal",
            "lumaco",
            "melipeuco",
            "nueva-imperial",
            "padre-las-casas",
            "perquenco",
            "pitrufquen",
            "puerto-saavedra",
            "puren",
            "renaico",
            "temuco",
            "teodoro-schmidt",
            "tolten",
            "traiguen",
            "victoria",
            "vilcun",
            "villarrica"
        ],
        "los-rios":[
            "corral",
            "futrono",
            "la-union",
            "lagoranco",
            "lanco",
            "los-lagos",
            "mafil",
            "mariquina",
            "paillaco",
            "panguipulli",
            "rio-bueno",
            "valdivia"
        ],
        "los-lagos":[
            "ancud",
            "calbuco",
            "castro",
            "chalico",
            "chonchi",
            "curaco-de-velez",
            "dalcahue",
            "fresia",
            "frutillar",
            "futaleufu",
            "hualaihue",
            "llanquihue",
            "maullin",
            "osorno",
            "palena",
            "puerto-montt",
            "puerto-octay",
            "puerto-varas",
            "puqueldon",
            "purranque"]
}

regiones = ["metropolitana"]

#comunas_prueba = ["vitacura-metropolitana", "las-condes-metropolitana", "providencia-metropolitana", "lo-barnechea-metropolitana"]
comunas_prueba = ["vitacura-metropolitana", "las-condes-metropolitana","providencia-metropolitana", "lo-barnechea-metropolitana"]

comunas = []
for region, lugares in regiones_de_chile.items():
    if region in regiones:
        for lugar in lugares:
            comunas.append(lugar+"-"+region)

comunas = comunas_prueba
opciones = [ "arriendo"] #"arriendo",

inmuebles = ["departamento","casa"]

estados = ["propiedades-usadas"]

'''
lat_min, lat_max = -33.411, -33.379
lon_min, lon_max = -70.605, -70.536
resolucion = 0.001

# Create a list of latitude ranges
latitud = [str(lat*resolucion - resolucion/2) + "*" + str(lat*resolucion + resolucion/2) 
           for lat in range(int(lat_min/resolucion), int(lat_max/resolucion))]
longitud = [str(lon*resolucion - resolucion/2) + "*" + str(lon*resolucion + resolucion/2) 
            for lon in range(int(lon_min/resolucion), int(lon_max/resolucion))]
'''

uf_pesos = 36274  # Define el valor de la UF en pesos chilenos.

errores = 0  # Inicializa una variable para contar errores.

# Crear un objeto tqdm para mostrar la barra de progreso
criterios = len(comunas)*len(opciones)*len(inmuebles)*len(estados)  # Calcula el número total de criterios a iterar.
progress_bar_total = tqdm(total=criterios, desc="Iterando por los criterios de búsqueda")  # Crea una barra de progreso para el proceso global.

if os.path.exists("Data_portal_inmobiliario.csv"):  # Comprueba si ya existe un archivo CSV con datos antiguos.
    data_antigua = pd.read_csv("Data_portal_inmobiliario.csv")  # Lee los datos antiguos desde el archivo CSV.

else:
    # Si no existe un archivo CSV, construye una URL específica y obtén datos iniciales.
    url_especifica = f"https://www.portalinmobiliario.com/{opciones[0]}/{inmuebles[0]}/{estados[0]}/melipilla-metropolitana/"
    data_antigua = obtener_data(obtener_texto(url_especifica))

# Comienza a iterar a través de diferentes combinaciones de criterios.
for comuna in comunas:
    for opcion in opciones:
        for inmueble in inmuebles:
            for estado in estados:
                
                # Pausamos para evitar request demasiado seguidos.
                sleep(np.random.randint(1,20)/10)
                
                buscar = 1
                
                url_especifica = f"https://www.portalinmobiliario.com/{opcion}/{inmueble}/{estado}/{comuna}/_Desde_{buscar}_NoIndex_True"  # Reemplaza con la URL que desees
               
                try:    
                    resultados = obtener_resultados(obtener_texto(url_especifica ))
                except:
                    resultados = 0
                
                if resultados > 2000:
                    print(f"La {opcion}, {inmueble}, {estado}, {comuna} debe ser segmentada, debido a que supera el límite de 42 páginas del portal")
                    resultados = 2001
                
                if resultados > 0:
                    # Crear un objeto tqdm para mostrar la barra de progreso
                    progress_bar = tqdm(total=resultados, desc=f"Extrayendo {opcion}, {inmueble}, {estado}, {comuna}")
                    
                    data = obtener_data(obtener_texto(url_especifica))
                    
                    progress_bar_total.update(1)
                    
                    while buscar <= resultados :
                        
                        # Pausamos para evitar request demasiado seguidos.
                        sleep(np.random.randint(1,5)/10)
                        
                        buscar += 48
                        
                        url_especifica = f"https://www.portalinmobiliario.com/{opcion}/{inmueble}/{estado}/{comuna}/_Desde_{buscar}_NoIndex_True"  # Reemplaza con la URL que desees
                        
                        try: 
                            data_hoja = obtener_data(obtener_texto(url_especifica))
                            data = pd.concat([data,data_hoja])
                            
                        except Exception as e:
                            print(f"Error al procesar {url_especifica}: {e}") 
                            errores +=1
                            
                        
    
                        progress_bar.update(48)
                        
                    # Eliminamos traslapes
                    data = data.drop_duplicates()
                    
                    
                    data["Comuna"]= comuna
                    data["Tipo oferta"]= opcion
                    data["Tipo inmueble"] = inmueble
                    data["Estado"] = estado
                    #data["latitud"] = str((float(lat.split("*")[0]) + float(lat.split("*")[1]))/2)
                    #data["longitud"] = str((float(lon.split("*")[0]) + float(lon.split("*")[1]))/2)
                    data["Fecha extraccion"] = "{}/{}/{}".format(datetime.now().day, datetime.now().month, datetime.now().year)

                    
                    data_antigua = pd.concat([data_antigua,data])
                    
                    # Eliminamos traslapes
                    data_antigua = data_antigua.drop_duplicates()
         
            
print("Errores: ",errores)

data_antigua = data_antigua.dropna(subset=['Comuna'])

data_antigua.replace("ñ","n", regex=True).to_csv("Data_portal_inmobiliario_2.csv",index=False)

