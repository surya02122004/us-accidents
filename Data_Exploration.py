import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def run():
    st.header("Dataset Exploration")
    df = pd.read_csv("data/US_Accidents_March23.csv")
    
    st.write("Preview of dataset")
    st.dataframe(df.head())

    st.write("Missing Values Heatmap")
    plt.figure(figsize=(14, 8))  # Larger figure size for better visibility
    sns.heatmap(df.isnull(),
                cbar=False,
                cmap="viridis",  # Better contrast colormap
                yticklabels=False,
                xticklabels=True,
                linewidths=0.5,  # Adds grid lines for clarity
                linecolor='gray')
    plt.xticks(rotation=45, ha='right')  # Rotate x labels for readability
    plt.title("Missing Values Heatmap")
    st.pyplot(plt.gcf())
    