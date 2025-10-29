import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import gaussian_kde

def run():
    st.header("Univariate Analysis")
    df = pd.read_csv("data/US_Accidents_preprocessed.csv")

    # Select column without default selection
    col = st.selectbox("Select Column", options=["--Choose a column--"] + list(df.columns))
    if col == "--Choose a column--":
        st.info("Please select a column to analyze.")
        return

    is_numeric = pd.api.types.is_numeric_dtype(df[col])

    if is_numeric:
        # Numerical column: plot histogram with optional KDE
        show_kde = st.checkbox("Include KDE plot in histogram", value=False)

        fig = px.histogram(df, x=col, nbins=30, title=f"Histogram of {col}")

        if show_kde:
            # Calculate KDE values manually
            data_series = df[col].dropna()
            kde = gaussian_kde(data_series)
            x_min, x_max = data_series.min(), data_series.max()
            x_vals = np.linspace(x_min, x_max, 200)
            y_vals = kde(x_vals)
            bin_width = (x_max - x_min) / 30
            y_vals_scaled = y_vals * len(data_series) * bin_width
            # Add KDE line trace on histogram
            fig.add_scatter(x=x_vals, y=y_vals_scaled, mode='lines', name='KDE', line=dict(color='red'))

        st.plotly_chart(fig, use_container_width=True)

    else:
        # Categorical column: plot top 10 counts bar chart
        counts = df[col].value_counts().nlargest(10)
        fig = px.bar(counts, x=counts.index.astype(str), y=counts.values,
                     title=f"Top 10 counts of {col}", labels={col: col, "y": "Count"})
        st.plotly_chart(fig, use_container_width=True)
