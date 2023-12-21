import streamlit as st
from PIL import Image
import pandas as pd
import requests
from credentials import API_KEY
from utils import Get_Coords, transform_df_map, distance_station, marker_station
from geopandas import GeoDataFrame, points_from_xy
import folium 
from haversine import haversine, Unit
from streamlit_folium import folium_static

image = Image.open('estación_de_gasolina.jpeg')

st.sidebar.image(image, caption="Estación de servicio APP", width=256)
app_mode = st.sidebar.selectbox("Elije una opción", ["Ejecutar aplicación", "Sobre mi"])

if app_mode == 'Ejecutar aplicación':
    st.title('Estación cercana')
    st.markdown('Descripción APP')
    
    df_map = pd.read_csv('DATASET_FINAL.csv')
    cities = list(df_map['City'].unique())
    
    c1,c2,c3,c4,c5 = st.columns((1,6,6,6,1))
    
    choose_city = c2.selectbox("Elije una ciudad", cities)
    
    central_location = c2.text_input('Localización central', 'Caupolicán 399, Los Ángeles')
    
    DEVELOPER_KEY = API_KEY
    
    if len(central_location) != 0 :
        R = Get_Coords(central_location, API_KEY)
        geo_source = R[1], R[2]

        unit = 'Km'
        rad = c4.slider('Radio', 1,3,1)
        
        df_city = df_map[df_map['City'] == choose_city]
        df_city.reset_index(inplace= True)
        df_city.drop(columns= 'index', inplace= True)
        
        df_city = transform_df_map(df_city)
        
        results = distance_station(geo_source, df_city, rad, unit)
        results.reset_index(inplace=True)
        results.drop(columns='index', inplace=True)
        products = list(results['Type_oil'].unique())
        
        gdf_results = GeoDataFrame(results, geometry= points_from_xy(results.LNG, results.LAT))
        
        choose_product = c3.selectbox('Tipo de combustible', products)
        
        if c3.button('Mostrar mapa'):
            
            gdf_results2 = gdf_results[gdf_results['Type_oil'] == choose_product]
            gdf_results2 = gdf_results2.reset_index()
            gdf_results2 = gdf_results2.drop(columns='index')
            icono = 'usd'
            
            m = folium.Map([geo_source[0], geo_source[1]], zoom_start= 15)
            
            folium.Circle(
                radius= int(rad) * 1000,
                location = [geo_source[0], geo_source[1]],
                color = 'green',
                fill = 'green').add_to(m)

            folium.Marker(
                location = [geo_source[0], geo_source[1]],
                icon= folium.Icon(color='black', icon_color='white', icon= 'home', prefix= 'glyphicon'),
                popup= 'Municipalidad</br>').add_to(m)

            marker_station(gdf_results2, m, unit, choose_product, 'usd')
            
            st.markdown('**Mapa de Estaciones de Combustible**')
            folium_static(m)
            
     
        