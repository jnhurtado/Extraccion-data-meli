# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 23:10:14 2023

@author: jhurt
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.metrics import mean_squared_error

from keras.models import Sequential
from keras.layers import Dense, Dropout

from xgboost import XGBRegressor




def split_train_test(X, y, test_size=0.2, random_state=50):
    # Dividir los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    return X_train, X_test, y_train, y_test

def filter_outliers(data, threshold_low=0.1, threshold_high=0.9):
    # Calcula la métrica de precio por dormitorio
    data['Precio por Dormitorio'] = data['Valor pesos'] / data['Dormitorios']
    
    # Calcula los límites para los outliers
    lower_limit = data['Precio por Dormitorio'].quantile(threshold_low)
    upper_limit = data['Precio por Dormitorio'].quantile(threshold_high)
    
    # Filtra los datos basados en los límites
    filtered_data = data[
        (data['Precio por Dormitorio'] >= lower_limit) &
        (data['Precio por Dormitorio'] <= upper_limit)
    ]
    return filtered_data

def plot_learning_curve(estimator, X, y):
    train_sizes, train_scores, test_scores = learning_curve(
        estimator, X, y, train_sizes=np.linspace(0.1, 1.0, 10), cv=5)

    train_scores_mean = np.mean(train_scores, axis=1)
    test_scores_mean = np.mean(test_scores, axis=1)

    plt.figure(figsize=(8, 6))
    plt.title('Curva de Aprendizaje')
    plt.xlabel('Tamaño del conjunto de entrenamiento')
    plt.ylabel('Puntuación')
    plt.grid()

    plt.plot(train_sizes, train_scores_mean, 'o-', color='r', label='Entrenamiento')
    plt.plot(train_sizes, test_scores_mean, 'o-', color='g', label='Validación')

    plt.legend(loc='best')
    plt.show()
    
def graficar(y_test, y_train, modelos):
    
    Resultado =[]
    Columns = ["Nombre","Modelo","[RMSE","Overfit]","[R","Overfit]","Pendiente"]
    i = 1
    
    for nombre in modelos:
        predicted = modelos[nombre][0]
        predicted_train = modelos[nombre][1]
        
        # Cálculo de la correlación
        correlation = np.corrcoef(y_test, predicted)[0, 1]
        correlation_train = np.corrcoef(y_train, predicted_train)[0, 1]

        # Ajuste de la línea de tendencia
        m, b = np.polyfit(y_test, predicted, 1)
        
        # Crear el gráfico de dispersión con la línea de tendencia
        plt.scatter(y_test/1000000, predicted/1000000, label='Datos')
        plt.plot(y_test/1000000, (m*y_test + b)/1000000, color='red', label='Línea de tendencia')
        
        rmse = np.round(np.sqrt(mean_squared_error(y_test, predicted)),0)
        rmse_train = np.round(np.sqrt(mean_squared_error(y_train, predicted_train)),0)

        r = np.round(correlation,4)
        r_train = np.round(correlation_train,4)
        
        overfit_r = r_train - r
        overfit_rmse = -(rmse_train - rmse)
        
        Resultado.append([nombre,"model"+str(i),rmse,overfit_rmse,r, overfit_r,np.round(m,4)])
        i += 1
        
        # Agregar información de RMSE, R y la pendiente al gráfico
        plt.text(0.7, 0.05, f'RMSE: {rmse}', ha='left', va='center', transform=plt.gca().transAxes)
        plt.text(0.7, 0.1, f'R: {r:.3f}', ha='left', va='center', transform=plt.gca().transAxes)
        plt.text(0.7, 0.15, f'Pendiente: {m:.3f}', ha='left', va='center', transform=plt.gca().transAxes)
 
        # Etiquetas de los ejes y título
        plt.xlabel('Precio Original [$ millones]')
        plt.ylabel('Precio Pronosticado [$ millones]')
        plt.title(f'Gráfico de Dispersión: {nombre}')
        plt.legend()
        
        # Mostrar el gráfico
        plt.show()
    
    Resultados = pd.DataFrame(Resultado, columns=Columns)
    print(Resultados)
   

comuna = "providencia-metropolitana"
tipo_oferta = "arriendo"
tipo_inmueble = "departamento"

# Lee los datos antiguos desde el archivo CSV.
data = pd.read_csv("Data_portal_inmobiliario.csv")  

Data_filtrada = data[data["Tipo inmueble"] == tipo_inmueble][data['Tipo oferta'] == tipo_oferta][data["Comuna"]==comuna].dropna()

#Aplica el filtro a los datos filtrados previamente
Data_filtrada = filter_outliers(Data_filtrada)

data_x = Data_filtrada[['Metros Utiles', 'Dormitorios']]

data_x["Banos"] = pd.to_numeric(Data_filtrada['Baños'].replace({' banos': '', ' bano': ''}, regex=True), errors='coerce')

# Datos de ejemplo
# Matriz X con dos variables independientes
X = np.array(data_x)
# Variable dependiente y
y = np.array(Data_filtrada["Valor pesos"])



X_train, X_test, y_train, y_test = split_train_test(X, y)


# Crear el modelo de regresión lineal
model1 = LinearRegression()

# Modelo Random Forest
model2 = RandomForestRegressor(n_estimators=100)

# Modelo Ridge Regressor
alpha=0.50
model3 = Ridge(alpha=alpha) 

# Modelo Deep Learning Fully Connected
units=50
model4 = Sequential()
model4.add(Dense(units=units, input_dim=3))  # Capa densa con una unidad de salida y tres de entrada
model4.add(Dropout(0.5))
model4.add(Dense(units=units/2, input_dim=units))
model4.add(Dropout(0.5))
model4.add(Dense(units=1, input_dim=units/2))
model4.compile(optimizer='adam', loss='mean_squared_error')

# Modelo XGBRegressor
model5 = XGBRegressor()

# Modelo KNeighbors
model6 = KNeighborsRegressor()


# Entrenar el modelo con los datos
model1.fit(X_train, y_train)
model2.fit(X_train, y_train)
model3.fit(X_train, y_train)
model4.fit(X_train, y_train, epochs=100, verbose=0)
model5.fit(X_train, y_train)
model6.fit(X_train, y_train)

# Coeficientes de la regresión (pendientes)
print("Coeficientes:", model1.coef_)
# Término independiente (intercepto)
print("Término independiente:", model1.intercept_)

# Predicción utilizando el modelo entrenado
predicted1 = model1.predict(X_test), model1.predict(X_train)
predicted2 = model2.predict(X_test), model2.predict(X_train)
predicted3 = model3.predict(X_test), model3.predict(X_train)
predicted4 = model4.predict(X_test).reshape(-1), model4.predict(X_train).reshape(-1)
predicted5 = model5.predict(X_test), model5.predict(X_train)
predicted6 = model6.predict(X_test), model6.predict(X_train)

#print("Predicciones:", predicted1)

modelos = {"Regresor Lineal": predicted1,
           "Random Forest": predicted2,
           f"Ridge alfa = {alpha}": predicted3,
           f"DL-FCL units = {units}": predicted4,
           "XRboost Regresor": predicted5,
           "KNeighbors Regresor": predicted6
           }

print("""
################################################################

Modelo predicción Portal Inmobiliario

""")  
graficar(y_test,y_train, modelos)

print(" ")
m, d, b = 45,2,2

print(f"Depto {m} m2, {d}d, {b}b: ")
print("Regresor Lineal: ", np.round(model1.predict([[m, d, b]])[0],0), " pesos")
print("Random Forest: ", np.round(model2.predict([[m, d, b]])[0],0), " pesos")
print(f"Regresor Ridge, alfa = {alpha}: ", np.round(model3.predict([[m, d, b]])[0],0), " pesos")
print(f"Fully Connected, units = {units}: ", np.round(model4.predict([[m, d, b]]).reshape(-1)[0],0), " pesos")
print("Regresor XRboost: ", np.round(model5.predict([[m, d, b]]).reshape(-1)[0],0), " pesos")
print("Regresor KNeighbors: ", np.round(model6.predict([[m, d, b]]).reshape(-1)[0],0), " pesos")


plot_learning_curve(model1, X, y)
