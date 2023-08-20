import requests
import json
import streamlit as st
API_KEY = st.secrets['openweather_api']


def get_weather(lat, lng, mode):

    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&appid={API_KEY}&units=metric"
    response = requests.request("GET", url, headers={}, data={})

    weatherData = json.loads(response.text)
    #print(weatherData)
    if mode == 'Current':
        temp = weatherData['current']['temp']
        pressure = weatherData['current']['pressure']
        humid = weatherData['current']['humidity']
        icon = weatherData['current']['weather'][0]['icon']
        if 'rain' in weatherData['current']:
            rain = weatherData['current']['rain']['1h'] * 24 / 1000 #average 1 day and mL
        else :
            rain = 0
    elif mode == 'Today(Average)':
        selected_data = weatherData['daily'][0]
        #temp = weatherData['current']['temp']
        raw_temp = selected_data['temp']
        temp = sum([raw_temp['day'], raw_temp['night'], raw_temp['morn'], raw_temp['eve']]) / 4
        pressure = selected_data['pressure']
        humid = selected_data['humidity']
        icon = selected_data['weather'][0]['icon']
        if 'rain' in selected_data:
            rain = selected_data['rain']
        else :
            rain = 0
    
    
    
    return {'temperature' : temp, 'pressure' : pressure, 'humidity' : humid, 'rain' : rain, 'icon' : icon}

def getAirData(lat, lng):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lng}&appid={API_KEY}"
    response = requests.request("GET", url, headers={}, data={})

    airData = json.loads(response.text)
    return airData['list'][0]['components']['pm2_5']


#13.74478887431261, 100.56404536486895

if __name__ == "__main__":
    #print(get_weather(13.74478887431261, 100.56404536486895, 'current'))
    print(getAirData(13.74478887431261, 100.56404536486895))