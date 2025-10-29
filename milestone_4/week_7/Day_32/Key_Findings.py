import streamlit as st
import pandas as pd
import plotly.express as px

def run():
    st.header("Key Findings & Summary Dashboard")

    df = pd.read_csv("data/US_Accidents_preprocessed.csv")

    # --- Basic Metrics ---
    st.subheader("Summary Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Accidents Analyzed", f"{len(df):,}")
    if 'Hour' in df.columns:
        peak_hour = df['Hour'].mode()[0]
        col2.metric("Peak Accident Hour", peak_hour)
    else:
        col2.warning("Hour column missing")
    if 'Severity' in df.columns:
        high_severity_count = df[df["Severity"] >= 3].shape[0]
        col3.metric("High Severity Accidents (Severity≥3)", f"{high_severity_count:,}")
    else:
        col3.warning("Severity column missing")

    # --- Top 5 States ---
    st.subheader("Top 5 Accident-Prone States")
    if 'State' in df.columns:
        top_states = df['State'].value_counts().nlargest(5)
        fig_states = px.bar(top_states, x=top_states.index, y=top_states.values,
                            labels={"x":"State", "y":"Number of Accidents"},
                            title="Top 5 States by Accident Counts",
                            color=top_states.values, color_continuous_scale='Viridis')
        fig_states.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_states, use_container_width=True)
    else:
        st.warning("State column missing")

    # --- Top 5 Cities ---
    st.subheader("Top 5 Accident-Prone Cities")
    if 'City' in df.columns:
        top_cities = df['City'].value_counts().nlargest(5)
        fig_cities = px.bar(top_cities, x=top_cities.index, y=top_cities.values,
                            labels={"x":"City", "y":"Number of Accidents"},
                            title="Top 5 Cities by Accident Counts",
                            color=top_cities.values, color_continuous_scale='Plasma')
        fig_cities.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_cities, use_container_width=True)
    else:
        st.warning("City column missing")

    # --- Top 5 Weather Conditions ---
    st.subheader("Top 5 Weather Conditions During Accidents")
    if 'Weather_Condition' in df.columns:
        weather_counts = df['Weather_Condition'].value_counts().nlargest(5)
        fig_weather = px.pie(names=weather_counts.index, values=weather_counts.values,
                             title="Top 5 Weather Conditions During Accidents",
                             color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_weather, use_container_width=True)
    else:
        st.warning("Weather_Condition column missing")

    # --- Road Surface / Feature Conditions ---
    st.subheader("Top 5 Road Surface / Feature Conditions in Accidents")
    road_features = ['Bump', 'Crossing', 'Give_Way', 'Junction', 'No_Exit',
                     'Railway', 'Roundabout', 'Station', 'Stop', 'Traffic_Calming',
                     'Traffic_Signal', 'Turning_Loop']
    existing_features = [feat for feat in road_features if feat in df.columns]

    if existing_features:
        feature_counts = {}
        for feat in existing_features:
            count = df[df[feat] == 1].shape[0] if df[feat].dtype != 'bool' else df[df[feat]].shape[0]
            feature_counts[feat] = count
        feature_series = pd.Series(feature_counts).sort_values(ascending=False).nlargest(5)

        fig_features = px.bar(feature_series, x=feature_series.index, y=feature_series.values,
                              labels={"x":"Road Feature", "y":"Accident Count"},
                              title="Top 5 Road Surface / Feature Conditions",
                              color=feature_series.values,
                              color_continuous_scale='Turbo')
        fig_features.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_features, use_container_width=True)
    else:
        st.info("Road surface / feature condition data not available in dataset.")

    st.caption("Patterns are from DV RoadSafe dataset's exploratory and spatial analyses.")
