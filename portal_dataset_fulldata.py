# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 21:47:33 2023

@author: jhurt
"""

from bs4 import BeautifulSoup as soup
import pandas as pd
import numpy as np
import requests
from tqdm import tqdm
from time import sleep
import os
from datetime import datetime
import json


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
    soup1 = soup(html, 'html.parser')
    resultados = soup1.find('span', {'class': 'ui-search-search-result__quantity-results'})
    resultados = resultados.text if resultados else print("No se pudo obtener los resultados")
    
    return int(resultados.replace(" resultados", "").replace(".",""))
 

   
data = pd.read_csv("Data_portal_inmobiliario.csv")  # Lee los datos antiguos desde el archivo CSV.


for link in data["URL"]:
    
    url = link
    

    pageSoup = soup(obtener_texto(url), 'html.parser')
    if(pageSoup.find('h4', {"class" : "media-block-title"})):
        no1_text = pageSoup.find('h4', {"class" : "media-block-title"})
        no1 = no1_text.text.strip()
        
        no2_text = pageSoup.find('div', {'class' :"data-sheet-column data-sheet-column-address"})
        no2 = no2_text.text.strip()
        no2 = no2.replace(u'\n', u' ')
        no3_text = pageSoup.find('div', {'class':"propiedad-descr"})
        no3 =  no3_text.text.strip()
        
        no4_text = pageSoup.findAll('p', {'class':"operation-internal-code"})
        no4 = no4_text[0].text.strip()
        
        if(pageSoup.find('p', {'class':"amoblada"})):
            no5_text = pageSoup.find('p', {'class':"amoblada"})
            no5 = no5_text.text.strip()
        else:
            no5 = "N/A"
        
        no6_text = pageSoup.find('p', {'class':"price"})
        no6 = no6_text.text.strip()
        
        no7_text = pageSoup.find('p', {'class':"price-ref"})
        no7 = no7_text.text.strip()
        
        no8 = no4_text[1].text.strip()
        
        
        no9_text = pageSoup.find('div', {'class' :"data-sheet-column data-sheet-column-programm"})
        no9w = no9_text.p.text.strip()
        num = no9w.find(';')
        no9 = no9w[0]
        no10 = no9w[num+1]
        
        no11_text = pageSoup.find('div', {'class' :"data-sheet-column data-sheet-column-area"})
        no11w = no11_text.p.text.strip()
        no11w = no11w.replace(u'\xa0', u' ')
        num1 = no11w.find('til')
        no11 = no11w[0:num1+3]
        no12 = no11w[num1+3:]
        
        doc = browser.find_element_by_xpath('.//button[@id="btnVerContacto"]')
        browser.execute_script("window.scrollTo(0, window.scrollY + 400)")
        doc.click()
        time.sleep(2)
        pageSoup = soup(browser.page_source, 'html.parser')
        
        if(pageSoup.find('p', {'class' :'operation-owner-name'})):
            no13_text = pageSoup.find('p', {'class' :'operation-owner-name'})
            no13 = no13_text.text.strip()
            no13 = no13.replace(u'\xa0', u' ')
        else:
            no13 = "N/A"
        if(pageSoup.find('p', {'class' :'operation-contact-email overlai-elipsis'})):
            no14_text = pageSoup.find('p', {'class' :'operation-contact-email overlai-elipsis'})
            no14 = no14_text.text.strip()
        else:
            no14 = 'N/A'
        if(pageSoup.find('p', {'class' :'operation-owner-phone'})):
            no15_text = pageSoup.find('p', {'class' :'operation-owner-phone'})
            no15 = no15_text.text.strip()
            no15 = no15.replace(u'\xa0', u' ')
        else:
            no15 = "N/A"  
        if(pageSoup.find('p', {'class' :'operation-owner-address'})):
            no16_text = pageSoup.find('p', {'class' :'operation-owner-address'})
            no16 = no16_text.text.strip()
            no16 = no16.replace(u'\n', u' ')
        else:
            no16 = "N/A"
        
                
        ser = pd.Series([url1, no1, no2, no3, no4, no5, no6, no7, no8, no9, no10, no11, no12, no13, no14, no15, no16], index =['Link', 'Ubicación', 'Descripción de ubicación la propiedad', 'Descripción', 'Código', 'Tipo de propiedad', 'Valor en $ (Pesos)', 'Valor en UF', 'Fecha de publicación', 'Dormitorios',
                                        'Baños', 'Mt2 construido', 'Mt2 Terreno', 'Nombre contacto', 'Correo contacto', 'Teléfono contacto', 'Ubicación contacto'])
        profile = profile.append(ser, ignore_index=True)
    else:
        url2 = "https://www.portalinmobiliario.com" + link.a['href']
        browser.get(url2)
        pageSoup = soup(browser.page_source, 'html.parser')
        browser.execute_script("window.scrollTo(0, window.scrollY + 400)")
        doc = browser.find_element_by_xpath('.//button[@class="btn btn-link prj-phones-show-all"]')
        doc.click()
        time.sleep(2)
        pageSoup = soup(browser.page_source, 'html.parser')
        no10_text = pageSoup.find('ul', {'class' :'prj-phones-list'})
        no10 = no10_text.text.strip()
        
        no1_text = pageSoup.find('span', {'class' :'prj-price-range-lower'})
        no1 = no1_text.text.strip()
        
        no2_text = pageSoup.findAll('span', {'class' :'project-feature-details'})
        no2 = no2_text[1].text.strip()
        no3 = no2_text[2].text.strip()
        no4 = no2_text[3].text.strip()
        browser.execute_script("window.scrollTo(0, window.scrollY - 200)")
        
        no5_text = pageSoup.find('p', {'class' :'prj-map-addr-obj'})
        no5 = no5_text.text.strip()
        
        
        browser.execute_script("window.scrollTo(0, window.scrollY + 600)")
        no6_text = pageSoup.find('div', {'class' :'col-xs-12 col-md-8'})
        no6 = no6_text.text.strip()
        no6 = no6.replace(u'\n', u' ')
        if(pageSoup.find('span', {'class': 'prj-code'})):
            no7_text = pageSoup.find('span', {'class': 'prj-code'})
            no7 = no7_text.text.strip()
        else:
            no7 = 'N/A'
        ser = pd.Series([url2, no5, 'Dereccion' + no5, no6, no7, 'N/A', 'N/A', no1, 'N/A', no2, no3, no4, 'N/A', 'N/A', 'N/A', no10, 'N/A'], index =['Link', 'Ubicación', 'Descripción de ubicación la propiedad', 'Descripción', 'Código', 'Tipo de propiedad', 'Valor en $ (Pesos)', 'Valor en UF', 'Fecha de publicación', 'Dormitorios',
                                            'Baños', 'Mt2 construido', 'Mt2 Terreno', 'Nombre contacto', 'Correo contacto', 'Teléfono contacto', 'Ubicación contacto'])
        profile = profile.append(ser, ignore_index=True)
    print('done')





print(profile)
filename = 'freportalinmobiliario.xlsx'
writer = pd.ExcelWriter(filename, engine='xlsxwriter')
profile.to_excel(writer, index=False)
writer.save()


data_antigua["Fecha extraccion"] = "{}/{}/{}".format(datetime.now().day, datetime.now().month, datetime.now().year)

data_antigua = data_antigua.dropna(subset=['Comuna'])

data_antigua.replace("ñ","n", regex=True).to_csv("Data_portal_inmobiliario.csv",index=False)

