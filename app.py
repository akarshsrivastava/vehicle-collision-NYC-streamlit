import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
#st.title("hello world!")
#st.markdown("### my first streamlit dashboard")

DATA_URL = (
"C:/Users/Admin/Desktop/project/Motor_Vehicle_Collisions_-_Crashes.csv"
)

st.title("Motor Vehicle Collisions in New York ")
st.markdown("This application is a streamlit dashboard that can be used to analyze motor vehicle collisions in NYC 🚗💥")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True) #streamlit can't work with missing data
    lowercase = lambda x:str(x).lower()
    data.rename(lowercase, axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time': 'date/time'},inplace=True)
    return data

data = load_data(100000)
original_data = data
#st.write(data.columns)

st.header('Where are the most people injured in NYC?')
injured_people = st.slider("Number of persons injured in vehicle collisions",0,19)
st.map(data.query('injured_persons >= @injured_people')[["latitude", "longitude"]].dropna(how='any'))

st.header('How many collisions occur during a given time of day?')
#hour = st.selectbox("Hour to look at",range(0,24),1)
#hour = st.sidebar.slider("Hour to look at",0,23)
hour = st.slider("Hour to look at",0,23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("vehicle collisions between %i:00 and %i:00" % (hour,(hour + 1) % 24))

midpoint = (np.average(data['latitude']),np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v10",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude":midpoint[1],
        "zoom":11,
        "pitch":80,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time','latitude','longitude']],
            get_position=['longitude', 'latitude'],
            extruded=True,
            pickable=True,
            radius=50,
            elevation_scale=4,
            elevation_range=[0,1000],
        ),
    ],
))

st.subheader("Breakdown of collisions by minute between %i:00 and %i:00" % (hour,(hour+1)%24))

filtered = data[
    (data['date/time'].dt.hour >= hour ) & (data['date/time'].dt.hour < (hour + 1 ))
]

hist = np.histogram(filtered['date/time'].dt.minute,bins=60,range=(0,60))[0]
chart_data = pd.DataFrame({'minute':range(60),'crashes':hist})
fig = px.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
st.write(fig)

st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("select type of people", ["Pedestrians","Cyclists","Motorists"])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[['on_street_name', 'injured_pedestrians']].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:5])

if select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[['on_street_name', 'injured_cyclists']].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:5])

if select == 'Motorists':
    st.write(original_data.query("injured_motorists >= 1")[['on_street_name', 'injured_motorists']].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:5])

if st.checkbox("Show raw data", False):
    st.subheader('Raw data')
    st.write(data)
