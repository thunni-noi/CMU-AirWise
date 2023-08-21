import streamlit as st
from streamlit_js_eval import get_geolocation
from streamlit_folium import st_folium
import folium
from weather_api import get_weather, getAirData
#from folium.features import CustomIcon
from run_model import model_predict
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
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
#st.write(globals())

DEFAULT_LOC = [18.789660, 98.984398]
if "map_markers" not in st.session_state: st.session_state["map_markers"] = []
if "use_default_loc" not in st.session_state : st.session_state.use_default_loc = False
if "param" not in st.session_state: st.session_state["param"] = None
if "prediction" not in st.session_state: st.session_state["prediction"] = None
if 'sel_lat' not in st.session_state : st.session_state['sel_lat'] = 0
if 'sel_lng' not in st.session_state : st.session_state['sel_lng'] = 0

#!REMOVED - may update it sometimes later
_ = '''
@st.cache_data(experimental_allow_widgets=True)
def get_location_data():
    global refetch_gps
    refetch_gps = False
    if not ('gps_retries' in globals()) : gps_retries = 0
    loc = get_geolocation()
    if gps_retries >= 15:
        st.error('We cannot fetch your data! Please ensure that we can access your gps ')
        gps_retries -= 1 #To cap the waiting time to 15 sec
    time.sleep(3 + gps_retries) 
    try :
        output = loc['coords']['latitude'], loc['coords']['longitude']
        st.success('Fetching GPS successfully!')
        return output
    except:
        st.warning('Cannot fetch your gps data! ; Please enable gps then press the button below.')
        gps_retries += 1
        return ["n/a", "n/a"]
'''
    
#def google_get_location(location):
geolocator = Nominatim(user_agent='cmuAirwise')
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

 

#f st.button('Refresh GPS Data'):
#    st.cache_data.clear()
#    lat, lng = get_location_data()

lat, lng = DEFAULT_LOC
if 'map_center' not in st.session_state : st.session_state['map_center'] = [lat, lng]



#if 'sel_lat' not in globals():
#    sel_lat, sel_lng = [0, 0]
#ookie_manager = get_cookie_manager()

#st.write(cookie_manager.get_all())
#if 'location' not in st.session_state: st.session_state['location'] = None
#if 'weather' not in st.session_state: st.session_state['weather'] = None
#if 'pm25' not in st.session_state: st.session_state['pm25'] = None
#if 'prediction' not in st.session_state: st.session_state['prediction'] = None


st.title('AirWise')
st.header('Forecasting PM2.5 Prowess with OpenWeatherAPI')
st.markdown('Source code available on [GitHub](https://github.com/thunni-noi/CMU-AirWise)')
st.caption('Weather data is pulled from openweatherAPI free package which has limited usage per day.')
#st.sidebar.button('Resel all', on_click=st.experimental_rerun)
st.caption(f'Default latitude is {lat} and longitude is {lng}')
st.subheader('Pick your location to fetch the weather from.')
st.caption('Due to software limitation, user need to click on update button below to update the map!')

gps_marker = folium.Marker([lat, lng],
                                popup="Current Location",
                                tooltip="Current Location",
                                icon=folium.Icon(icon='diamond',icon_color='white', color='blue', prefix='fa'))
st.session_state['map_markers'].append(gps_marker)

map_col, weather_col = st.columns(2)
with map_col:
    
    #with st.echo(code_location = 'above'):
    m = folium.Map(location= [lat,lng] , zoom_start=16)
    fg = folium.FeatureGroup(name="Markers")
    m.add_child(folium.LatLngPopup())
    for markers in st.session_state['map_markers']:
        fg.add_child(markers)
    f_map = st_folium(
        m,
        center=st.session_state['map_center'],
        feature_group_to_add=fg,
        width=1000,
        height=1200
        )
    
    sub_map_col1, sub_map_col2, sub_map_col3 = st.columns([0.25,0.25,0.5])
    if sub_map_col1.button('Back to default location'):
        st.session_state['map_center'] = [lat, lng]
    #st.write(f_map)
    #st.write(st.session_state['map_center'])
    if sub_map_col2.button('Update map', help='Dued to software limitation, the program need to run some function to make the map update and this button is made for that!'):
        None
    

#search_lat, search_lng = [0,0]
    
if f_map.get("last_clicked"):
    if not st.session_state.use_default_loc:
        st.session_state['sel_lat'] = f_map['last_clicked']['lat']
        st.session_state['sel_lng'] = f_map['last_clicked']['lng']
    

def search_location(name):
    global searched_lat
    global searched_lng
    geo_location = geolocator.geocode(name)
    if (hasattr(geo_location, 'latitude')):
        searched_lat =  geo_location.latitude
        searched_lng =  geo_location.longitude
        #f_map.center = {'lat' : searched_lat, 'lng' : searched_lng}
        serach_marker = folium.Marker([searched_lat, searched_lng],
                        popup="Searched Location",
                        tooltip=name,
                        icon=folium.Icon(icon='diamond',icon_color='white', color='red', prefix='fa'))
        st.session_state['map_markers'][1] = serach_marker
        st.session_state['map_center'] = [searched_lat, searched_lng]
        st.success(f'Location of {name} has been successfully fetched! Click on the map to update the map.')
    else:
        st.warning('Your location is not valid. Please ensure that spelling is correct or use latidue and longitude instaad.')
        searched_lat = 0
        searched_lng = 0
    
with st.form('Location search'):
        #loc_searh_c1, loc_search_c2 = st.columns([0.8,0.2])
        location_name = st.text_input('Search for location', value='มหาวิทยาลัยเชียงใหม่')
        location_seach_submit = st.form_submit_button('Search')

if location_seach_submit:
        search_location(location_name)
        st.session_state.use_default_loc = False
        st.session_state['sel_lat'] = searched_lat
        st.session_state['sel_lng'] = searched_lng

weather_container = st.container()

with weather_col:
        st.subheader('How to use:')
        st.write('Search for location in the search bar below(Need to press submit manually) or click on the map to auto-input latitude and longitude')
        st.write('Select whether you want data pulled from API to to data current or the average of today')
        st.write('Press "Run" button.')

with weather_container:
    st.write('Weather data configuration')
    weather_mode = st.selectbox('Weather mode', ['Current', 'Today(Average)'], index=1)
    
    
    form_c1, form_c2 = st.columns(2)
    if use_default_loc := st.checkbox('Use default location', key='use_default_loc'):
        st.session_state['sel_lat'] = lat
        st.session_state['sel_lng'] = lng
    with form_c1 :
        st.session_state['sel_lat'] = st.text_input('Latitude' , str(st.session_state['sel_lat']), disabled=st.session_state.use_default_loc)
    with form_c2 :
        st.session_state['sel_lng'] = st.text_input('Longitude' , str(st.session_state['sel_lng']), disabled=st.session_state.use_default_loc)

    
    weather_submitted = st.button('Run')
    if weather_submitted:
        st.success(f"Stored position: {st.session_state['sel_lat']}, {st.session_state['sel_lng']}")
        sel_location = [st.session_state['sel_lat'], st.session_state['sel_lng']]
        #st.session_state['location'] = [st.session_state['sel_lat'], sel_lng]
        with st.spinner('Fetching data location'):
            weather_data = get_weather(sel_location[0], sel_location[1], weather_mode)
            air_data = getAirData(sel_location[0], sel_location[1])
            #weather_data = get_weather(st.session_state['location'][0], st.session_state['location'][1], weather_mode)
            #air_data = getAirData(st.session_state['location'][0], st.session_state['location'][1])
            predicted = model_predict(weather_data['humidity'], weather_data['temperature'], weather_data['pressure'], weather_data['rain'])
            st.session_state['param'] = [weather_data, air_data]
            #st.session_state['pm25'] = air_data
            st.session_state['prediction'] = predicted
    



if st.session_state['param'] is not None:
    weather_data = st.session_state['param'][0]
    air_data = st.session_state['param'][1]
    predicted = st.session_state['prediction']
    with weather_col:
            _, center_img_c, _ = st.columns([0.1,0.2,0.7])
            image_url = f"http://openweathermap.org/img/wn/{weather_data['icon']}@4x.png"
            center_img_c.image(image_url)
            #st.image(image_url)
            st.metric("Temperature", f"{round(weather_data['temperature'],2)} °C")
            st.metric("Humidity", f"{round(weather_data['humidity'],2)} %")
            st.metric("Pressure", f"{round(weather_data['pressure'],2)} hPa")
            st.metric("Rain" , f"{weather_data['rain']} mL/day")
            weatherColSub1, weatherColSub2 = st.columns(2)
            weatherColSub1.metric("Predicted PM2.5", f"{str(predicted)[:5]} μg/m³")
            weatherColSub2.metric("PM2.5", f"{air_data} μg/m³", delta=round(air_data - predicted, 2), delta_color="inverse")
            
            diff = abs(predicted - air_data)
            if predicted - air_data < 0:
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
    
        