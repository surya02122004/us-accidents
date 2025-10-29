import streamlit as st
import pandas as pd
from scipy.stats import ttest_ind, chi2_contingency, pearsonr

def run():
    st.header("Insight Extraction & Hypothesis Testing with Statistical Validation")

    df = pd.read_csv("data/US_Accidents_preprocessed.csv", nrows=40000)

    ## Insight 1
    st.subheader("Insight 1: Effect of Weather Conditions on Accident Severity")
    weather_groups = df.groupby("Weather_Condition")["Severity"].mean().sort_values(ascending=False).head(10)
    st.bar_chart(weather_groups)
    st.markdown("**Hypothesis:** Different weather conditions lead to different average accident severities.")
    if "Clear" in df["Weather_Condition"].unique() and "Rain" in df["Weather_Condition"].unique():
        clear = df[df["Weather_Condition"] == "Clear"]["Severity"]
        rain = df[df["Weather_Condition"] == "Rain"]["Severity"]
        _, p = ttest_ind(clear, rain, nan_policy='omit')
        if p < 0.05:
            st.success(f"Theory Proven TRUE: Significant difference found (p={p:.4f}). Weather impacts severity.")
        else:
            st.warning(f"Theory Proven FALSE: No significant difference (p={p:.4f}). Weather does not impact severity.")
    else:
        st.info("Insufficient data for test between 'Clear' and 'Rain'.")

    ## Insight 2
    st.subheader("Insight 2: Accident Frequency by Hour of Day")
    hourly_counts = df['Hour'].value_counts().sort_index()
    st.line_chart(hourly_counts)
    st.markdown("**Hypothesis:** Accident frequency differs between morning rush hours (7-9am) and late night (12-3am).")
    rush_hours = df[df['Hour'].between(7,9)].shape[0]
    night_hours = df[df['Hour'].between(0,3)].shape[0]
    st.write(f"Accidents 7-9am: {rush_hours}, 12-3am: {night_hours}")
    if rush_hours > night_hours:
        st.success("Theory Proven TRUE: More accidents during morning rush hours.")
    else:
        st.warning("Theory Proven FALSE: More accidents not observed during morning rush hours.")

    ## Insight 3
    st.subheader("Insight 3: Correlation Between Temperature and Accident Severity")
    temp_bins = pd.cut(df["Temperature(F)"], bins=[-50, 0, 32, 50, 70, 90, 110, 150], right=False)
    temp_severity = df.groupby(temp_bins)["Severity"].mean().sort_index()
    temp_severity = temp_severity.reset_index()
    temp_severity[temp_severity.columns[0]] = temp_severity[temp_severity.columns[0]].astype(str)
    temp_severity = temp_severity.set_index(temp_severity.columns[0])
    st.bar_chart(temp_severity)
    corr, corr_p = pearsonr(df["Temperature(F)"].dropna(), df["Severity"].dropna())
    st.success(f"Pearson correlation: {corr:.3f} (p={corr_p:.4e}) - {'Weak' if abs(corr)<0.3 else 'Moderate/Strong'} relationship.")
    st.markdown("**Theory:** Higher temperature extremes influence accident severity. Correlation shows the strength of this relationship.")

    ## Insight 4
    st.subheader("Insight 4: Accident Counts by Visibility Range")
    visibility_bins = [0, 1, 2, 5, 10, 20, df["Visibility(mi)"].max()]
    visibility_labels = ["<1mi", "1-2mi", "2-5mi", "5-10mi", "10-20mi", ">20mi"]
    df['Visibility_Range'] = pd.cut(df["Visibility(mi)"], bins=visibility_bins, labels=visibility_labels, include_lowest=True)
    visibility_counts = df['Visibility_Range'].value_counts().reindex(visibility_labels)
    st.bar_chart(visibility_counts)
    st.markdown("**Hypothesis:** Low visibility (<2mi) leads to higher accident frequency.")
    df['Low_Visibility'] = df['Visibility_Range'].isin(["<1mi", "1-2mi"])
    contingency_table = pd.crosstab(df['Low_Visibility'], df['Severity'])
    _, p_vis, _, _ = chi2_contingency(contingency_table)
    if p_vis < 0.05:
        st.success(f"Theory Proven TRUE: Significant association between low visibility and accident severity (p={p_vis:.4f}).")
    else:
        st.warning(f"Theory Proven FALSE: No significant association found (p={p_vis:.4f}).")

    ## Insight 5
    st.subheader("Insight 5: Accident Counts: Rain vs No Rain")
    df['Is_Rain'] = df['Weather_Condition'].str.lower().str.contains('rain', na=False)
    rain_counts = df['Is_Rain'].value_counts()
    st.bar_chart(rain_counts)
    st.markdown("**Hypothesis:** Rain increases accident frequency.")
    contingency_rain = pd.crosstab(df['Is_Rain'], df['Severity'])
    _, p_rain, _, _ = chi2_contingency(contingency_rain)
    if p_rain < 0.05:
        st.success(f"Theory Proven TRUE: Rain significantly affects accident severity/frequency (p={p_rain:.4f}).")
    else:
        st.warning(f"Theory Proven FALSE: Rain does not significantly affect accidents (p={p_rain:.4f}).")

    ## Insight 6
    st.subheader("Insight 6: Correlation between Humidity and Accident Severity")
    df_clean = df.dropna(subset=["Humidity(%)", "Severity"])
    corr_hum, p_hum = pearsonr(df_clean["Humidity(%)"], df_clean["Severity"])
    st.write(f"Pearson correlation (Humidity vs Severity): {corr_hum:.3f} (p={p_hum:.4e})")
    if p_hum < 0.05:
        st.success("Theory Proven TRUE: Significant correlation between humidity and severity.")
    else:
        st.warning("Theory Proven FALSE: No significant correlation between humidity and severity.")

    # Insight 7: Does Pressure Affect Accident Severity?
    st.subheader("Insight 7: Does Pressure Affect Accident Severity?")
    df_clean_pressure = df.dropna(subset=["Pressure(in)", "Severity"])
    corr_pressure, p_pressure = pearsonr(df_clean_pressure["Pressure(in)"], df_clean_pressure["Severity"])
    st.write(f"Pearson correlation (Pressure vs Severity): {corr_pressure:.3f} (p={p_pressure:.4e})")
    st.markdown("**Hypothesis:** Atmospheric pressure correlates with accident severity.")
    if p_pressure < 0.05:
        st.success(f"Theory Proven TRUE: Significant correlation between pressure and severity (p={p_pressure:.4f}).")
    else:
        st.warning(f"Theory Proven FALSE: No significant correlation between pressure and severity (p={p_pressure:.4f}).")

    # Insight 8: Effect of Road Features on Accident Severity
    st.subheader("Insight 8: Effect of Road Features on Accident Severity")

    road_features = ['Bump', 'Crossing', 'Give_Way', 'Junction', 'No_Exit',
                    'Railway', 'Roundabout', 'Station', 'Stop',
                    'Traffic_Calming', 'Traffic_Signal', 'Turning_Loop']

    existing_features = [feat for feat in road_features if feat in df.columns]

    if existing_features:
        results = []
        for feat in existing_features:
            # Filter rows where feature is True / 1 vs False / 0
            with_feat = df[df[feat] == 1]["Severity"].dropna()
            without_feat = df[df[feat] == 0]["Severity"].dropna()
            
            # Perform t-test if both groups have data
            if len(with_feat) > 10 and len(without_feat) > 10:
                stat, p = ttest_ind(with_feat, without_feat, nan_policy='omit')
                theory = "TRUE" if p < 0.05 else "FALSE"
                results.append((feat, len(with_feat), len(without_feat), p, theory))
            else:
                results.append((feat, len(with_feat), len(without_feat), None, "Insufficient data"))

        # Display Results
        for feat, n_with, n_without, p, theory in results:
            st.write(f"Feature: **{feat}**")
            st.write(f"  Cases with feature: {n_with}, without feature: {n_without}")
            if p is not None:
                if theory == "TRUE":
                    st.success(f"  p-value={p:.4f} → Theory Proven TRUE: Road feature significantly affects severity.")
                else:
                    st.warning(f"  p-value={p:.4f} → Theory Proven FALSE: No significant impact on severity.")
            else:
                st.info("  Not enough data to test hypothesis.")
    else:
        st.info("No road feature columns found in data for this insight.")
