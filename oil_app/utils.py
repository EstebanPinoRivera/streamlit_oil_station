import pandas as pd 
import requests
from bs4 import BeautifulSoup
from credentials import API_KEY
import json
import time
import random

from haversine import haversine, Unit
import folium
from geopandas import GeoDataFrame, points_from_xy

def Get_Coords(address, API_KEY):
    url = f'https://geocode.search.hereapi.com/v1/geocode?q={address}&apiKey={API_KEY}'
    
    try:
        response = requests.get(url).json()
        CleanAddress = response['items'][0]['title'].upper()
        LAT = response['items'][0]['position']['lat']
        LNG = response['items'][0]['position']['lng']
        
        results = [CleanAddress, LAT, LNG]
        
    except:
        
        results = ['Not found', 'NA', 'NA']
        
    return results

def cal_dist(geo_source, point2, unit):
    
    if unit == 'Km':
        distance = haversine(geo_source, point2, Unit.KILOMETERS)
    elif unit == 'm':
        distance = haversine(geo_source, point2, Unit.METERS)
    elif unit == 'miles':
        distance = haversine(geo_source, point2, Unit.MILES)
        
    return round(distance, 2)

def distance_station(geo_source, df, radio, unit):
    
    distance = []
    source = []
    
    for i in range(len(df)):
        distance.append(cal_dist(geo_source, df['POINT'][i], unit))
        source.append(geo_source)
    
     # Create a copy of the original DataFrame
    new_df = df.copy()
    
    # Add new columns to the DataFrame: 'SOURCE' and 'DISTANCE'
    new_df['SOURCE'] = source
    new_df['DISTANCE'] = distance
    
    # Filter the DataFrame based on the calculated distances within the given radius
    new_df = new_df[new_df['DISTANCE'] <= radio]
    
    # Reset the index of the DataFrame
    new_df = new_df.reset_index()
    
    # Drop the old index column
    new_df = new_df.drop(columns='index')
    
    # Return the filtered and sorted DataFrame based on distance
    return new_df.sort_values(by='DISTANCE', ascending=True)

def transform_df_map(df):
    # Initialize an empty list to store coordinates
    coords = []

    # Loop through the DataFrame
    for i in range(len(df)):
        try:
            # Try to convert 'LAT' and 'LNG' values to float and create a coordinate tuple
            coord = float(df['LAT'][i]), float(df['LNG'][i])
            coords.append(coord)
        except:
            # If conversion is not possible, append 'EMPTY' to the list
            coords.append('EMPTY')

    # Add a new 'POINT' column to the DataFrame with the coordinates
    df['POINT'] = coords
    
    # Filter out rows where 'POINT' is labeled as 'EMPTY'
    df = df[df['POINT'] != 'EMPTY']
    
    # Reset the index of the DataFrame
    df = df.reset_index()
    
    # Drop the old index column
    df = df.drop(columns='index')
    
    # Create a copy of the DataFrame
    new_df = df.copy()

    # Return the transformed DataFrame
    return new_df

def marker_station(df, mapa, unit, oil, icono):
    # Filter the DataFrame based on the specified oil type
    df = df[df['Type_oil'] == oil]
    df = df.reset_index()
    df = df.drop(columns='index')

    # Iterate through the rows of the DataFrame
    for i in range(len(df)):
        # Check if the current row has the minimum price
        if df['Price'][i] == df['Price'].min():
            # Create HTML content for the popup
            html = f"""<b>ESTACIÓN:</b> {df.Station_name[i]} <br>
                       <b>PRODUCTO:</b> {df.Type_oil[i]} <br>
                       <b>PRECIO:</b> {df.Price[i]} <br>
                       <b>DISTANCE:</b> {round(df.DISTANCE[i], 2)}<br>
                       <b>DIRECCION:</b> {df.Station_address[i]}<br>
                       <b>UNIT:</b> {unit}<br>"""
            iframe = folium.IFrame(html, figsize=(6, 3))
            popup = folium.Popup(iframe)

            # Add a marker to the map with a dark green color and the specified icon
            folium.Marker(location=[float(df['LAT'][i]), float(df['LNG'][i])],
                          icon=folium.Icon(color='darkgreen', icon_color='white', icon=icono, prefix='glyphicon'),
                          popup=popup).add_to(mapa)
        # Check if the current row has the maximum price
        elif df['Price'][i] == df['Price'].max():
            # Create HTML content for the popup
            html = f"""<b>ESTACIÓN:</b> {df.Station_name[i]} <br>
                       <b>PRODUCTO:</b> {df.Type_oil[i]} <br>
                       <b>PRECIO:</b> {df.Price[i]} <br>
                       <b>DISTANCE:</b> {round(df.DISTANCE[i], 2)}<br>
                       <b>DIRECCION:</b> {df.Station_address[i]}<br>
                       <b>UNIT:</b> {unit}<br>"""
            iframe = folium.IFrame(html, figsize=(6, 3))
            popup = folium.Popup(iframe)

            # Add a marker to the map with a dark red color and the specified icon
            folium.Marker(location=[float(df['LAT'][i]), float(df['LNG'][i])],
                          icon=folium.Icon(color='darkred', icon_color='white', icon=icono, prefix='glyphicon'),
                          popup=popup).add_to(mapa)
        # If the current row does not have the minimum or maximum price
        else:
            # Create HTML content for the popup
            html = f"""<b>ESTACIÓN:</b> {df.Station_name[i]} <br>
                       <b>PRODUCTO:</b> {df.Type_oil[i]} <br>
                       <b>PRECIO:</b> {df.Price[i]} <br>
                       <b>DISTANCE:</b> {round(df.DISTANCE[i], 2)}<br>
                       <b>DIRECCION:</b> {df.Station_address[i]}<br>
                       <b>UNIT:</b> {unit}<br>"""
            iframe = folium.IFrame(html, figsize=(6, 3))
            popup = folium.Popup(iframe)

            # Add a marker to the map with an orange color and the specified icon
            folium.Marker(location=[float(df['LAT'][i]), float(df['LNG'][i])],
                          icon=folium.Icon(color='orange', icon_color='white', icon=icono, prefix='glyphicon'),
                          popup=popup).add_to(mapa)
    
    # The function does not return anything; it modifies the 'mapa' object in place
    return
