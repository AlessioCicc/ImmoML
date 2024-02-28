# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import requests
import folium
from folium.plugins import HeatMap
from streamlit.components.v1 import html
import algoritmo

# Function to load data (dummy example)
def load_data(n_rows):
    data = pd.DataFrame({
        'first_column': np.random.rand(n_rows),
        'second_column': np.random.rand(n_rows)
    })
    return data
    
# Funzione per ottenere le coordinate geografiche da un indirizzo
def get_geocode(address):
    # Qui puoi usare l'API di Google Maps o un'altra API di geocoding
    # Ad esempio, con OpenStreetMap (Nominatim API):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            lat = data[0]['lat']
            lon = data[0]['lon']
            return lat, lon
        else:
            # Imposta valori di default per lat e lon
            lat, lon = 41.8797737, 12.4674504
    else:
        # Imposta valori di default per lat e lon
        lat, lon = 41.8797737, 12.4674504

# Streamlit page configuration (optional)
st.set_page_config(page_title='Your App Title')

# Sidebar for user inputs
st.sidebar.header('Parametri di Ricerca Immobili')

# 1. Location Input
location = st.sidebar.text_input('Inserisci Indirizzo', key="address_input")

if location:
    lat, lon = get_geocode(location)
    if lat and lon:
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
condition = st.sidebar.selectbox('Stato', ['Buono', 'Nuova Costruzione', 'Da Ristrutturare'])

# 6. Floor Input
floor = st.sidebar.selectbox('Piano', ['Seminterrato', 'Piano terra', 'Intermedi', 'Attico'])

# 7. Elevator Input
elevator = st.sidebar.selectbox('Ascensore', ['SI', 'NO'])

# 8. Garage Input
garage = st.sidebar.selectbox('Garage', ['SI', 'NO'])

# 9. Energy Efficiency Range Input
# Assuming energy efficiency classes range from A to G
energy_efficiency = st.sidebar.select_slider('Efficienza Energetica', options=['A', 'B', 'C', 'D', 'E', 'F', 'G'])

# 10. Year of Construction Range Input
current_year = pd.Timestamp.now().year
min_year, max_year = st.sidebar.slider('Range Anno di Costruzione', 1900, current_year, (1980, current_year))

# Chiama la funzione process_data
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
st.write('I risultati della ricerca verranno visualizzati qui...')

# Display data on the app
st.write('### Risultato', 10) #processed_data)

# Crea una mappa centrata sull'indirizzo specificato
mappa = folium.Map(location=[lat, lon], zoom_start=13)

# Ottieni i dati per la heatmap
if location:
    lat, lon = get_geocode(location)
    if lat and lon:
        lat, lon = float(lat), float(lon)
        heatmap_data = algoritmo.generate_dummy_heatmap_data(lat, lon)
        heat_data = [[row['lat'], row['lon'], row['value']] for row in heatmap_data]

# Aggiungi la heatmap alla mappa
HeatMap(heat_data).add_to(mappa)

# Converti la mappa Folium in HTML
mappa_html = mappa._repr_html_()

# Visualizza la mappa in Streamlit
st_folium(mappa_html, width=700, height=500)
