import pandas as pd
import plotly.express as px
import streamlit as st

# Load dataset (assume CSV in working directory)
dataset_path = "C:/Users/win10/Desktop/US_Accidents_March23.csv"
df = pd.read_csv(dataset_path)

def plot_accidents_sampled(df, location_col='State', sample_size=50000):
    counts = df[location_col].value_counts().head(5)
    top5_locations = counts.index.tolist()
    df['is_top5'] = df[location_col].isin(top5_locations)

    # Sample data to reduce size
    if len(df) > sample_size:
        df_sample = df.sample(sample_size, random_state=42)
    else:
        df_sample = df

    fig = px.scatter(
        df_sample,
        x='Start_Lng',
        y='Start_Lat',
        color='is_top5',
        labels={'Start_Lng': 'Longitude', 'Start_Lat': 'Latitude', 'is_top5': 'Top 5 Accident-Prone'},
        title=f'Accident Scatter Plot Highlighting Top 5 {location_col}s',
        opacity=0.6,
        hover_data=[location_col]
    )
    st.plotly_chart(fig)

st.title('Accident Data Visualization')

location_option = st.selectbox('Select Location Type', ['State', 'City'])

plot_accidents_sampled(df, location_col=location_option)
