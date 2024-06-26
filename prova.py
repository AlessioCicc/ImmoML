# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from opencage.geocoder import OpenCageGeocode
import pickle
import sklearn

key = 'a7bd6bd2c7604ba287219157b6bc946b'
geocoder = OpenCageGeocode(key)

#dev
filename = 'model&preproc.pkl'
with open(filename, 'rb') as infile:
    loaded_model, preproc = pickle.load(infile)
X = ['surface', 'latitude', 'longitude', 'bathrooms', 'rooms', 'condition', "piano", "ascensore", "garage"]
#surface               float64
#latitude              float64
#longitude             float64
#bathrooms              object
#rooms                  object
#condition              object
#piano                 float64
#ascensore              object
#garage                 object
#price                 float64

X = np.array([[150.0, 41.12, 12.5776, 2, 4, 3, 0, 0, 1],], dtype=object)
X_norm = preproc.transform(X)
prezzo = loaded_model.predict(X_norm)
#print(prezzo)
#fine dev

# Inizializza lat e lon con valori di default
lat, lon, formatted_address = 41.8797737, 12.4674504, "None"  # Posizione di default (es. Roma)

# Function to load data (dummy example)
def load_data(n_rows):
    data = pd.DataFrame({
        'first_column': np.random.rand(n_rows),
        'second_column': np.random.rand(n_rows)
    })
    return data
    
# Funzione per ottenere le coordinate geografiche da un indirizzo
def get_geocode(address):
    results = geocoder.geocode(address)
    lat = results[0]['geometry']['lat']
    lon = results[0]['geometry']['lng']
    formatted_address = results[0]['formatted']
    return lat, lon, formatted_address

# Streamlit page configuration (optional)
st.set_page_config(page_title='Ricerca Immobili')

# Sidebar for user inputs
st.sidebar.header('Parametri di Ricerca Immobili')

# 1. Location Input
location = st.sidebar.text_input('Inserisci Indirizzo', key="address_input")

if location:
    lat, lon, formatted_address = get_geocode(location)
    if lat and lon:
        lat, lon = float(lat), float(lon)
    else:
        lat, lon = None, None
    if lat and lon and formatted_address:
        st.sidebar.write(f"{formatted_address}")
        st.sidebar.write(f"Latitudine: {lat}, Longitudine: {lon}")
    else:
        st.sidebar.write("Indirizzo non trovato o non valido")

# 2. Space Range Input
min_space, max_space = st.sidebar.slider('Seleziona Range Superficie (in mq)', 10, 500, (30, 100))

# 3. Number of Rooms Input
min_rooms, max_rooms = st.sidebar.slider('Seleziona Range Numero di Stanze', 1, 10, (2, 4))

# 4. Number of Bathrooms Input
min_bathrooms, max_bathrooms = st.sidebar.slider('Seleziona Range Numero di Bagni', 1, 5, (1, 2))

# 5. Condition Input
condition_s = st.sidebar.selectbox('Stato', ['Buono', 'Nuova Costruzione', 'Da Ristrutturare'])
condition_dict = {"Da Ristrutturare":0, "Buono":1, "buone condizioni":1,
            "ottimo":2, "ottime condizioni":2, "recente costruzione":2, "di ristrutturazione":3, "ristrutturato":3, "nuovo":4,
            "in costruzione":4, "nuove costruzioni":4, "Nuova Costruzione":4}
condition = condition_dict[condition_s]

# 6. Floor Input
floor_s = st.sidebar.selectbox('Piano', ['Seminterrato', 'Piano terra', 'Intermedi', 'Attico'])
floor_dict = {"Piano terra":0, "rialzato":1, "Seminterrato":1, "Intermedi":2, "Attico":3}
floor =  floor_dict[floor_s]

# 7. Elevator Input
elevator_s = st.sidebar.selectbox('Ascensore', ['SI', 'NO'])
elevator = 1 if elevator_s=="SI" else 0

# 8. Garage Input
garage_s = st.sidebar.selectbox('Garage', ['SI', 'NO'])
garage = 1 if garage_s=="SI" else 0

# 9. Energy Efficiency Range Input
# Assuming energy efficiency classes range from A to G
energy_efficiency = st.sidebar.select_slider('Efficienza Energetica', options=['A', 'B', 'C', 'D', 'E', 'F', 'G'])

# 10. Year of Construction Range Input
current_year = pd.Timestamp.now().year
min_year, max_year = st.sidebar.slider('Range Anno di Costruzione', 1900, current_year, (1980, current_year))

# Display the inputs
st.sidebar.write('### Parametri Selezionati')
st.sidebar.write(f'Indirizzo: {formatted_address}')
st.sidebar.write(f'Lat: {lat}; Lon: {lon}')
st.sidebar.write(f'Superficie: da {min_space} a {max_space} mq')
st.sidebar.write(f'Numero di Stanze: da {min_rooms} a {max_rooms}')
st.sidebar.write(f'Numero di Bagni: da {min_bathrooms} a {max_bathrooms}')
st.sidebar.write(f'Stato: {condition}')
st.sidebar.write(f'Piano: {floor}')
st.sidebar.write(f'Ascensore: {elevator}')
st.sidebar.write(f'Garage: {garage}')
st.sidebar.write(f'Efficienza Energetica: Classe {energy_efficiency}')
st.sidebar.write(f'Anno di Costruzione: da {min_year} a {max_year}')

# Main section
st.title('Applicazione per Ricerca Immobili')

# Placeholder for Data Display and Further Analysis
st.write(f'# Prezzo al metro quadro: {int(round(prezzo[0],0)):,} €/m²\n')
st.write(f'## Prezzo abitazione: {int(round(prezzo[0]*max_space, 0)):,} €')

# Ottieni i dati dal modello ML
#X = ['surface', 'latitude', 'longitude', 'bathrooms', 'rooms', 'condition', "piano", "ascensore", "garage"]
#surface               float64
#latitude              float64
#longitude             float64
#bathrooms              object
#rooms                  object
#condition              object
#piano                 float64
#ascensore              object
#garage                 object
#price                 float64

# Generazione liste di valori 
surface_values = np.linspace(min_space, max_space, 3, dtype=int) #tre valori equidistanti all'interno del range tra min_space e max_space
bathrooms_values = np.array(range(min_bathrooms, max_bathrooms + 1), dtype=object) #tutti i valori compresi tra min_bathrooms e max_bathrooms
rooms_values = np.array(range(min_rooms, max_rooms + 1), dtype=object) #tutti i valori compresi tra min_rooms e max_rooms




X_norm_list = [] 
for surface in surface_values:
    for bathrooms in bathrooms_values:
        for rooms in rooms_values:
            #X = ['surface', 'latitude', 'longitude', 'bathrooms', 'rooms', 'condition', "piano", "ascensore", "garage"]
            X = np.array([[surface, lat, lon, bathrooms, 4, 3, 0, 0, 1],], dtype=object)
            X_norm = preproc.transform(X)
            X_norm_list.append(X_norm)

# Conversione di X_norm_list in un DataFrame per una migliore visualizzazione
X_norm_df = pd.DataFrame([x.flatten() for x in X_norm_list])

# Mostra la tabella nel tuo app Streamlit
#st.write("Visualizzazione di X_norm_list:")
#st.dataframe(X_norm_df)

# TEMP
X = np.array([[60.0, 41.12, 12.5776, 2, 4, 3, 0, 0, 1],], dtype=object)
X_norm = preproc.transform(X)
prezzo = loaded_model.predict(X_norm)
st.write(f'X: {X}-- X_norm: {X_norm}-- Prezzo: {prezzo}')
X = np.array([[80.0, 41.12, 12.5776, 2, 4, 3, 0, 0, 1],], dtype=object)
X_norm = preproc.transform(X)
prezzo = loaded_model.predict(X_norm)
st.write(f'X: {X}-- X_norm: {X_norm}-- Prezzo: {prezzo}')
X = np.array([[100.0, 41.12, 12.5776, 2, 4, 3, 0, 0, 1],], dtype=object)
X_norm = preproc.transform(X)
prezzo = loaded_model.predict(X_norm)
st.write(f'X: {X}-- X_norm: {X_norm}-- Prezzo: {prezzo}')
X = np.array([[[80.0, 100.0], 41.12, 12.5776, 2, 4, 3, 0, 0, 1],], dtype=object)
X_norm = preproc.transform(X)
prezzo = loaded_model.predict(X_norm)
st.write(f'X: {X}-- X_norm: {X_norm}-- Prezzo: {prezzo}')



# Definisci il range di latitudine e longitudine
lat_range = np.linspace(lat - 0.05, lat + 0.05, num=10) # Modifica i valori secondo le tue esigenze
lon_range = np.linspace(lon - 0.05, lon + 0.05, num=10)

# Prepara la lista per le previsioni
predictions = []

# Calcola le previsioni per ogni punto nella griglia
for lat_point in lat_range:
    for lon_point in lon_range:
        X = np.array([[surface, lat_point, lon_point, 2, 4, 3, 0, 0, 1]], dtype=object)
        X_norm = preproc.transform(X)
        price = loaded_model.predict(X_norm)
        predictions.append([lat_point, lon_point, price[0]])  # Assumi che price[0] sia il prezzo previsto

# Crea la mappa
map = folium.Map(location=[lat, lon], zoom_start=13)

# Aggiungi la heatmap
HeatMap(predictions).add_to(map)

# Visualizza la mappa in Streamlit
st_folium(map, width=700, height=500)
