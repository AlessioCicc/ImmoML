# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pickle
import sklearn

#dev
filename = 'model&preproc.pkl'
with open(filename, 'rb') as infile:
    loaded_model, preproc = pickle.load(infile)
X = ['surface', 'latitude', 'longitude', 'bathrooms', 'rooms', 'condition', "piano", "ascensore", "garage"]
#bathrooms              object
#rooms                  object
#surface               float64
#price                 float64
#latitude              float64
#longitude             float64
#condition              object
#ascensore              object
#garage                 object
#piano                 float64
X = np.array([[150.0, 41.12, 12.5776, 2, 4, 3, 0, 0, 1],], dtype=object)
X_norm = preproc.transform(X)
prezzo = loaded_model.predict(X_norm)
#print(prezzo)
#fine dev

# Inizializza lat e lon con valori di default
lat, lon = 41.8797737, 12.4674504  # Posizione di default (es. Roma)

# Function to load data (dummy example)
def load_data(n_rows):
    data = pd.DataFrame({
        'first_column': np.random.rand(n_rows),
        'second_column': np.random.rand(n_rows)
    })
    return data
    
# Funzione per ottenere le coordinate geografiche da un indirizzo
def get_geocode(address):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            formatted_address = data[0].get('display_name', '')  # Ottiene l'indirizzo formattato
            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon, formatted_address
    return None, None, None

# Streamlit page configuration (optional)
st.set_page_config(page_title='Ricerca Immobili')

# Sidebar for user inputs
st.sidebar.header('Parametri di Ricerca Immobili')

# Input
location = st.sidebar.text_input('Inserisci Indirizzo', key="address_input")
lat, lon, formatted_address = get_geocode(location) if location else (None, None, None)

# Mostra informazioni indirizzo se disponibili
if all([lat, lon, formatted_address]):
    lat, lon = map(float, (lat, lon))
    st.sidebar.write(f"{formatted_address}")
    st.sidebar.write(f"Latitudine: {lat}, Longitudine: {lon}")

# Altri input della sidebar
input_dict = {
    'Superficie': st.sidebar.slider('Seleziona Range Superficie (in mq)', 10, 500, (30, 100)),
    'Stanze': st.sidebar.slider('Seleziona Range Numero di Stanze', 1, 10, (2, 4)),
    'Bagni': st.sidebar.slider('Seleziona Range Numero di Bagni', 1, 5, (1, 2)),
    'Stato': st.sidebar.selectbox('Stato', ['Buono', 'Nuova Costruzione', 'Da Ristrutturare']),
    'Piano': st.sidebar.selectbox('Piano', ['Seminterrato', 'Piano terra', 'Intermedi', 'Attico']),
    'Ascensore': st.sidebar.selectbox('Ascensore', ['SI', 'NO']),
    'Garage': st.sidebar.selectbox('Garage', ['SI', 'NO']),
    'Efficienza Energetica': st.sidebar.select_slider('Efficienza Energetica', options=['A', 'B', 'C', 'D', 'E', 'F', 'G']),
    'Anno di Costruzione': st.sidebar.slider('Range Anno di Costruzione', 1900, pd.Timestamp.now().year, (1980, pd.Timestamp.now().year))
}

# Visualizza i parametri selezionati
st.sidebar.write('### Parametri Selezionati')
for key, value in input_dict.items():
    st.sidebar.write(f'{key}: {value}')

# Chiama la funzione process_data
X = np.array([[max_space, lat, lon, max_bathrooms, max_rooms, condition, floor, elevator, garage],], dtype=object)
X_norm = preproc.transform(X)
prezzo = loaded_model.predict(X_norm)
#processed_data = algoritmo.process_data(location, min_space, max_space, min_rooms, max_rooms, min_bathrooms, max_bathrooms, condition, floor, elevator, garage, energy_efficiency, min_year, max_year)

# Display the inputs
st.sidebar.write('### Parametri Selezionati')
st.sidebar.write(f'Località: {location}')
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
st.title('Applicazione Streamlit per Ricerca Immobili')

# Placeholder for Data Display and Further Analysis
st.write(f'# Prezzo al metro quadro: {int(round(prezzo[0],0)):,} €/m²\n')
st.write(f'## Prezzo abitazione: {int(round(prezzo[0]*max_space, 0)):,} €')

# Crea una mappa centrata sull'indirizzo specificato
mappa = folium.Map(location=[lat, lon], zoom_start=13)

# Ottieni i dati dal modello ML
X = ['surface', 'latitude', 'longitude', 'bathrooms', 'rooms', 'condition', "piano", "ascensore", "garage"]
#bathrooms              object
#rooms                  object
#surface               float64
#price                 float64
#latitude              float64
#longitude             float64
#condition              object
#ascensore              object
#garage                 object
#piano                 float64

X_norm_list = [] 
for surface in range(min_space, max_space): 
    X = np.array([[100, lat, lon, 2, 4, 3, 0, 0, 1],], dtype=object)
    X_norm = preproc.transform(X)
    X_norm_list.append(X_norm)

prezzo = loaded_model.predict(X_norm)




# Ottieni i dati per la heatmap
if location:
    lat, lon, formatted_address = get_geocode(location)
    lat, lon = float(lat), float(lon) if lat and lon else (None, None)
    #if lat and lon:
        #heatmap_data = algoritmo.generate_dummy_heatmap_data(lat, lon)
        #heat_data = [[row['lat'], row['lon'], row['value']] for row in heatmap_data] if heatmap_data else []

# Aggiungi la heatmap alla mappa
#if heat_data:
#    HeatMap(heat_data).add_to(mappa)

# Visualizza la mappa in Streamlit
st_folium(mappa, width=700, height=500)
