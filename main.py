import streamlit as st
from streamlit_js_eval import get_geolocation
from streamlit_folium import st_folium
import folium
from weather_api import get_weather, getAirData
#from folium.features import CustomIcon
from run_model import model_predict
import time

st.set_page_config(
    page_title="CMU AirWise",
    page_icon='https://s3-ap-northeast-1.amazonaws.com/killy-image/linestamp/1f/1f13/1f131746571cc91986f8b868ed2946789402c741',
    layout='wide',
    menu_items={
        'Report a bug' : 'https://github.com/thunni-noi/bicycle-prediction/issues',
        'About' : 'https://github.com/thunni-noi/bicycle-prediction'
    }
)

#?init
if 'location' not in st.session_state: st.session_state['location'] = None
if 'weather' not in st.session_state: st.session_state['weather'] = None
if 'pm25' not in st.session_state: st.session_state['pm25'] = None
if 'prediction' not in st.session_state: st.session_state['prediction'] = None
    

@st.cache_data(experimental_allow_widgets=True)
def get_location_data():
    loc = get_geolocation()
    time.sleep(3)
    try :
        return loc['coords']['latitude'], loc['coords']['longitude']
    except:
        st.warning('Cannot fetch your gps data! ; Please enable gps then refresh the page.')
        st.button('Refresh GPS Data', on_click=get_location_data.clear)
        return [0, 0]
    
    
latitude, longitude = get_location_data()


st.title('AirWise')
st.header('Forecasting PM2.5 Prowess with OpenWeatherAPI')
st.caption('Weather data is pulled from openweatherAPI free package which has limited usage per day.')
#st.sidebar.button('Resel all', on_click=st.experimental_rerun)
st.caption(f'Your current latitude is {latitude} and longitude is {longitude}')
st.subheader('Pick your location to fetch the weather from.')

m = folium.Map(location=[latitude, longitude], zoom_start=16)
folium.Marker(
    [latitude, longitude],
    popup="Current Location",
    tooltip="Current Location",
    icon=folium.Icon(icon='diamond',icon_color='white', color='blue', prefix='fa')
).add_to(m)
m.add_child(folium.LatLngPopup())


map_col, weather_col = st.columns(2)
print()
with map_col:
 f_map = st_folium(m, width=1000, height=900)

selected_latitude, selected_longitude = custom_lat, custom_lng = [0, 0]
    
if f_map.get("last_clicked"):
    selected_latitude = f_map['last_clicked']['lat']
    selected_longitude = f_map['last_clicked']['lng']
    
weather_container = st.container()


with weather_container:
    st.write('Weather data configuration')
    weather_mode = st.selectbox('Weather mode', ['Current', 'Average Today'])
    form_c1, form_c2 = st.columns(2)
    if use_local := st.checkbox('Use current location', True):
        selected_latitude = latitude
        selected_longitude = longitude
    with form_c1 :
        selected_latitude = st.text_input('Latitude' , str(selected_latitude), disabled=use_local)
    with form_c2 :
        selected_longitude = st.text_input('Longitude' , str(selected_longitude), disabled=use_local)
    weather_submitted = st.button('Submit')
    if weather_submitted:
        st.success(f"Stored position: {selected_latitude}, {selected_longitude}")
        st.session_state['location'] = [selected_latitude, selected_longitude]
        with st.spinner('Fetching data location'):
            weather_data = get_weather(st.session_state['location'][0], st.session_state['location'][1], weather_mode)
            air_data = getAirData(st.session_state['location'][0], st.session_state['location'][1])
            predicted = model_predict(weather_data['humidity'], weather_data['temperature'], weather_data['pressure'], weather_data['rain'])
            st.session_state['weather'] = weather_data
            st.session_state['pm25'] = air_data
            st.session_state['prediction'] = predicted
    

if st.session_state['weather'] is not None:
    weather_data = st.session_state['weather']
    with weather_col:
            image_url = f"http://openweathermap.org/img/wn/{weather_data['icon']}@4x.png"
            st.image(image_url)
            #st.image(image_url)
            st.metric("Temperature", f"{weather_data['temperature']}°C")
            st.metric("Humidity", f"{weather_data['humidity']}%")
            st.metric("Pressure", f"{weather_data['pressure']}hPa")
            st.metric("Rain" , f"{weather_data['rain']} mL/day")
            weatherColSub1, weatherColSub2 = st.columns(2)
            weatherColSub1.metric("Predicted PM2.5", f"{st.session_state['prediction']} ug/m³")
            weatherColSub2.metric("PM2.5", f"{st.session_state['pm25']} ug/m³", delta=round(st.session_state['pm25'] - st.session_state['prediction'], 2), delta_color="inverse")
            
            diff = abs(st.session_state['prediction'] - st.session_state['pm25'])
            if st.session_state['prediction'] - st.session_state['pm25'] < 0:
                #posttext = "(better)"
                txt_color = "red"
            else : 
                #posttext = "(worse)"
                txt_color = "green"
                
            if diff >= 50:
                anomaly_lvl = "Very high"
            elif diff >= 25:
                anomaly_lvl = "High"
            elif diff >= 15:
                anomaly_lvl = "Medium"
            elif diff >= 5:
                anomaly_lvl = "Low"
            else :
                anomaly_lvl = "Very Low"
            
            st.header(f'Anomaly status')
            st.header(f' > **:{txt_color}[{anomaly_lvl}]**')
            #st.header(f':{txt_color}[{anomaly_lvl}]**')
        