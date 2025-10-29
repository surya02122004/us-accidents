import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from scipy.stats import chi2_contingency


def cramers_v(x, y):
    """Calculate Cramér's V statistic for categorical-categorical association."""
    confusion_matrix = pd.crosstab(x, y)
    chi2 = chi2_contingency(confusion_matrix)[0]
    n = confusion_matrix.sum().sum()
    phi2 = chi2 / n
    r, k = confusion_matrix.shape
    phi2corr = max(0, phi2 - ((k - 1)*(r - 1)) / (n - 1))
    rcorr = r - ((r - 1)**2) / (n - 1)
    kcorr = k - ((k - 1)**2) / (n - 1)
    if rcorr == 0 or kcorr == 0:
        return np.nan
    return np.sqrt(phi2corr / min((kcorr -1), (rcorr -1)))


def run():
    st.header("Comparative Analysis")

    df = pd.read_csv("data/US_Accidents_preprocessed.csv")

    # Separate numerical and categorical features + adjust for Severity
    num_features = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    cat_features = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

    # Chart type selection
    chart_type = st.selectbox("Select chart type", options=["Scatterplot", "Box Plot", "Heatmap"])

    if chart_type == "Scatterplot":
        # Scatterplot: only numerical features for X and Y
        feature_x = st.selectbox("X-axis (Numerical)", options=[''] + num_features, index=0)
        feature_y = st.selectbox("Y-axis (Numerical)", options=[''] + num_features, index=0)

        if feature_x == '' or feature_y == '':
            st.info("Please select both numeric X-axis and Y-axis features.")
            return

        fig = px.scatter(
            df,
            x=feature_x,
            y=feature_y,
            color="Severity",
            title=f"Scatterplot of {feature_x} vs {feature_y}",
            labels={feature_x: feature_x, feature_y: feature_y},
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Box Plot":
        # Box Plot: single numerical feature to visualize distribution grouped by Severity
        feature_y = st.selectbox("Select numerical feature for box plot", options=[''] + num_features, index=0)

        if feature_y == '':
            st.info("Please select a numerical feature to display box plot.")
            return

        fig = px.box(
            df,
            y=feature_y,
            color="Severity",
            title=f"Box Plot of {feature_y} grouped by Severity",
            labels={feature_y: feature_y, "Severity": "Severity"},
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    else:  # Heatmap
        heatmap_data_type = st.radio("Heatmap Data Type", options=["Numerical", "Categorical"])

        if heatmap_data_type == "Numerical":
            # Automatically use all numerical features + Severity
            features = [f for f in num_features if f != 'Severity']
            if 'Severity' in df.columns:
                features.append('Severity')
            if len(features) < 2:
                st.info("Not enough numerical features to plot correlation heatmap.")
                return
            
            corr_matrix = df[features].corr()

            fig = ff.create_annotated_heatmap(
                z=corr_matrix.values.round(2),
                x=list(corr_matrix.columns),
                y=list(corr_matrix.index),
                colorscale='Viridis',
                showscale=True,
                annotation_text=corr_matrix.values.round(2)
            )
            fig.update_layout(title="Numerical Correlation Heatmap with Severity")
            st.plotly_chart(fig, use_container_width=True)

        else:  # Categorical heatmap based on Cramér's V including Severity even if numerical
            features = cat_features.copy()
            # Include Severity forcibly regardless of dtype
            if 'Severity' in df.columns and 'Severity' not in features:
                features.append('Severity')
            
            if len(features) < 2:
                st.info("Not enough categorical features to plot Cramér's V heatmap.")
                return

            n = len(features)
            cramers_matrix = np.zeros((n, n))

            for i in range(n):
                for j in range(n):
                    if i == j:
                        cramers_matrix[i, j] = 1.0
                    else:
                        val = cramers_v(df[features[i]], df[features[j]])
                        cramers_matrix[i, j] = val if val is not np.nan else 0

            fig = ff.create_annotated_heatmap(
                z=cramers_matrix.round(2),
                x=features,
                y=features,
                colorscale='Viridis',
                showscale=True,
                annotation_text=cramers_matrix.round(2)
            )
            fig.update_layout(title="Categorical Correlation Heatmap with Severity (Cramér's V)")
            st.plotly_chart(fig, use_container_width=True)
