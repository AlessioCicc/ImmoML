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
    results = geocoder.geocode(query)
    lat = results[0]['geometry']['lat']
    lon = results[0]['geometry']['lng']
    formatted_address = results[0]['formatted']
    print(u'%f;%f;%s;%s' % (results[0]['geometry']['lat'],
                            results[0]['geometry']['lng'],
                            results[0]['components']['country_code'],
                            results[0]['annotations']['timezone']['name']))
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

# Chiama la funzione process_data
X = np.array([[max_space, lat, lon, max_bathrooms, max_rooms, condition, floor, elevator, garage],], dtype=object)
X_norm = preproc.transform(X)
prezzo = loaded_model.predict(X_norm)
#processed_data = algoritmo.process_data(location, min_space, max_space, min_rooms, max_rooms, min_bathrooms, max_bathrooms, condition, floor, elevator, garage, energy_efficiency, min_year, max_year)

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
