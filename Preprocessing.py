import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression
import time

def run():
    """Preprocessing page - main entry point"""
    
    # =====================================================================
    # PAGE HEADER
    # =====================================================================
    st.title("🧹 Data Preprocessing Pipeline")
    st.markdown("### Automated Data Cleaning & Feature Engineering")
    st.markdown("---")

    # Configuration inputs
    col1, col2 = st.columns(2)
    with col1:
        DATA_PATH = st.text_input(
            "📁 Input Data Path",
            value="data/US_Accidents_March23.csv",
            help="Path to your raw accident dataset CSV file"
        )
    with col2:
        OUTPUT_PATH = st.text_input(
            "💾 Output Data Path",
            value="data/US_Accidents_preprocessed.csv",
            help="Where to save the cleaned dataset"
        )

    st.markdown("---")

    # Start button
    if st.button("🚀 Start Preprocessing", type="primary", use_container_width=True):
        run_preprocessing_pipeline(DATA_PATH, OUTPUT_PATH)
    else:
        # Show pipeline overview
        st.markdown("### 📝 Pipeline Overview (15 Steps)")
        
        overview_text = """
        | Step | Operation | Purpose |
        |------|-----------|---------|
        | 1 | Load Data | Import the raw accident dataset |
        | 2 | Remove Duplicates | Eliminate duplicate records by ID |
        | 3 | Drop High Missingness | Remove columns with >30% missing values |
        | 4 | Drop Non-Analytical | Remove IDs and text fields |
        | 5 | Parse Temporal Data | Validate and convert timestamps |
        | 6 | Validate Geographic | Clean and validate coordinates |
        | 7 | Filter Severity | Keep only severity levels 1-4 |
        | 8 | Drop Low-Missing Rows | Remove rows with <3% missing |
        | 9 | Weather Imputation | Domain-specific imputation strategies |
        | 10 | Numeric Imputation | Fill remaining missing values |
        | 11 | Temporal Features | Create time-based features |
        | 12 | Categorical Encoding | Convert boolean features to integers |
        | 13 | Drop Redundant | Remove columns no longer needed |
        | 14 | Final Cleanup | Remove any remaining NaN values |
        | 15 | Save Data | Export preprocessed dataset |
        """
        st.markdown(overview_text)
        
        st.info("👆 Click the **Start Preprocessing** button above to begin the pipeline")


def run_preprocessing_pipeline(DATA_PATH, OUTPUT_PATH):
    """Main preprocessing pipeline function with animated step-by-step tracking"""
    
    # Create placeholders for dynamic updates
    progress_bar = st.progress(0)
    status_text = st.empty()
    metrics_container = st.container()
    
    # Metrics placeholders
    with metrics_container:
        col1, col2, col3, col4 = st.columns(4)
        metric1 = col1.empty()
        metric2 = col2.empty()
        metric3 = col3.empty()
        metric4 = col4.empty()
    
    log_lines = []  # Accumulate log entries
    log_placeholder = st.empty()  # Placeholder for scrollable log display

    def log_step(step, message, current_shape=None):
        entry = f"✓ Step {step}: {message}"
        if current_shape:
            entry += f" → Shape: {current_shape}"
        log_lines.append(entry)
        # Render accumulated logs inside scrollable container
        log_placeholder.markdown(
            "<div style='max-height:300px; overflow-y:auto; border:1px solid #ccc; padding:10px; font-family: monospace;'>"
            + "<br>".join(log_lines) +
            "</div>",
            unsafe_allow_html=True
        )

    def update_progress(step, total_steps, message, current_shape=None):
        """Update progress bar, status, and log"""
        progress = step / total_steps
        progress_bar.progress(progress)
        status_text.markdown(f"**Step {step}/{total_steps}:** {message}")
        log_step(step, message, current_shape)
        time.sleep(0.3)  # Animation delay

    def update_metrics(rows, cols, missing, step_num):
        """Update displayed metrics"""
        metric1.metric("Rows", f"{rows:,}", delta=None)
        metric2.metric("Columns", f"{cols}", delta=None)
        metric3.metric("Missing Values", f"{missing:,}", delta=None)
        metric4.metric("Progress", f"{step_num}/15 steps", delta=None)

    try:
        # STEP 1: LOAD DATA
        update_progress(1, 15, "Loading data...", None)
        df = pd.read_csv(DATA_PATH)
        initial_shape = df.shape
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 1)
        update_progress(1, 15, "Data loaded successfully", df.shape)

        # STEP 2: REMOVE DUPLICATES
        update_progress(2, 15, "Removing duplicates...", None)
        df = df.drop_duplicates(subset="ID")
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 2)
        update_progress(2, 15, "Duplicates removed", df.shape)

        # STEP 3: DROP HIGH MISSINGNESS COLUMNS (>30%)
        update_progress(3, 15, "Analyzing missing values...", None)
        missing_percent = round((df.isnull().sum() / df.shape[0]) * 100, 2)
        remove_cols = missing_percent[missing_percent > 30].index.tolist()
        df.drop(columns=remove_cols, inplace=True)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 3)
        update_progress(3, 15, f"Dropped {len(remove_cols)} high-missingness columns", df.shape)

        # STEP 4: DROP NON-ANALYTICAL COLUMNS
        update_progress(4, 15, "Removing non-analytical columns...", None)
        drop_cols = ["ID", "Source", "Description", "Street", "Country", 
                     "Zipcode", "Timezone", "Airport_Code", "Amenity"]
        drop_cols_existing = [col for col in drop_cols if col in df.columns]
        df = df.drop(columns=drop_cols_existing)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 4)
        update_progress(4, 15, f"Dropped {len(drop_cols_existing)} non-analytical columns", df.shape)

        # STEP 5: PARSE AND VALIDATE TEMPORAL DATA
        update_progress(5, 15, "Parsing temporal data...", None)
        df["Start_Time"] = pd.to_datetime(df["Start_Time"], errors="coerce")
        df["End_Time"] = pd.to_datetime(df["End_Time"], errors="coerce")
        rows_before = len(df)
        df = df.dropna(subset=["Start_Time", "End_Time"])
        rows_dropped = rows_before - len(df)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 5)
        update_progress(5, 15, f"Temporal data validated ({rows_dropped} invalid rows removed)", df.shape)

        # STEP 6: VALIDATE GEOGRAPHIC DATA
        update_progress(6, 15, "Validating geographic coordinates...", None)
        df['Start_Lat'] = pd.to_numeric(df['Start_Lat'], errors='coerce')
        df['Start_Lng'] = pd.to_numeric(df['Start_Lng'], errors='coerce')
        rows_before = len(df)
        df = df.dropna(subset=["Start_Lat", "Start_Lng"])
        rows_dropped = rows_before - len(df)
        df.rename(columns={'Start_Lat': 'Latitude', 'Start_Lng': 'Longitude'}, inplace=True)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 6)
        update_progress(6, 15, f"Geographic data validated ({rows_dropped} invalid rows removed)", df.shape)

        # STEP 7: FILTER SEVERITY CLASSES
        update_progress(7, 15, "Filtering severity classes...", None)
        rows_before = len(df)
        df = df[df["Severity"].isin([1, 2, 3, 4])]
        rows_dropped = rows_before - len(df)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 7)
        update_progress(7, 15, f"Severity classes filtered ({rows_dropped} outliers removed)", df.shape)

        # STEP 8: DROP ROWS WITH LOW MISSINGNESS (<3%)
        update_progress(8, 15, "Handling low-missingness rows...", None)
        missing_percent = (df.isnull().sum() / df.shape[0]) * 100
        low_missing_cols = missing_percent[(missing_percent > 0) & (missing_percent <= 3)].index.tolist()
        rows_before = len(df)
        if low_missing_cols:
            df.dropna(subset=low_missing_cols, inplace=True)
        rows_dropped = rows_before - len(df)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 8)
        update_progress(8, 15, f"Low-missingness rows dropped ({rows_dropped} rows removed)", df.shape)

        # STEP 9: TARGETED WEATHER IMPUTATION
        update_progress(9, 15, "Performing targeted weather imputation...", None)
        imputation_count = 0
        
        if 'Wind_Speed(mph)' in df.columns and df['Wind_Speed(mph)'].isnull().any():
            wind_median = df['Wind_Speed(mph)'].median()
            count = df['Wind_Speed(mph)'].isnull().sum()
            df['Wind_Speed(mph)'] = df['Wind_Speed(mph)'].fillna(wind_median)
            imputation_count += count
        
        if 'Precipitation(in)' in df.columns and df['Precipitation(in)'].isnull().any():
            count = df['Precipitation(in)'].isnull().sum()
            df['Precipitation(in)'] = df['Precipitation(in)'].fillna(0.0)
            imputation_count += count
        
        if 'Wind_Chill(F)' in df.columns and df['Wind_Chill(F)'].isnull().any():
            reg_features = ['Wind_Speed(mph)', 'Temperature(F)', 'Humidity(%)']
            if all(col in df.columns for col in reg_features):
                known_wc = df[df['Wind_Chill(F)'].notna()]
                unknown_wc = df[df['Wind_Chill(F)'].isna()]
                if len(unknown_wc) > 0:
                    X_train = known_wc[reg_features]
                    y_train = known_wc['Wind_Chill(F)']
                    reg = LinearRegression()
                    reg.fit(X_train, y_train)
                    X_pred = unknown_wc[reg_features]
                    predicted_wc = reg.predict(X_pred)
                    df.loc[df['Wind_Chill(F)'].isna(), 'Wind_Chill(F)'] = predicted_wc
                    imputation_count += len(unknown_wc)
        
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 9)
        update_progress(9, 15, f"Weather imputation complete ({imputation_count:,} values imputed)", df.shape)

        # STEP 10: GENERAL NUMERIC IMPUTATION
        update_progress(10, 15, "General numeric imputation...", None)
        num_cols = df.select_dtypes(include="number").columns.tolist()
        imputed_cols = []
        for col in num_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())
                imputed_cols.append(col)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 10)
        update_progress(10, 15, f"General imputation complete ({len(imputed_cols)} columns)", df.shape)

        # STEP 11: FEATURE ENGINEERING - TEMPORAL
        update_progress(11, 15, "Creating temporal features...", None)
        df["Duration_Minutes"] = (df["End_Time"] - df["Start_Time"]).dt.total_seconds() / 60
        df['Year'] = df["Start_Time"].dt.year
        df["Hour"] = df["Start_Time"].dt.hour
        df["DayOfWeek"] = df["Start_Time"].dt.weekday
        df["Month"] = df["Start_Time"].dt.month
        df["IsWeekend"] = df["DayOfWeek"].isin([5, 6]).astype(int)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 11)
        update_progress(11, 15, "Temporal features created (6 new features)", df.shape)

        # STEP 12: FEATURE ENCODING - CATEGORICAL
        update_progress(12, 15, "Encoding categorical features...", None)
        bool_cols = ["Roundabout", "Station", "Stop", "Traffic_Calming", 
                     "Traffic_Signal", "Turning_Loop"]
        encoded_count = 0
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(int)
                encoded_count += 1
        
        if "Sunrise_Sunset" in df.columns:
            df["IsDay"] = (df["Sunrise_Sunset"] == "Day").astype(int)
            encoded_count += 1
        
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 12)
        update_progress(12, 15, f"Categorical encoding complete ({encoded_count} features)", df.shape)

        # STEP 13: DROP REDUNDANT FEATURES
        update_progress(13, 15, "Removing redundant features...", None)
        redundant_cols = ["Start_Time", "End_Time", "Weather_Timestamp", 
                          "Civil_Twilight", "Nautical_Twilight", 
                          "Astronomical_Twilight", "Sunrise_Sunset"]
        redundant_cols_existing = [col for col in redundant_cols if col in df.columns]
        df = df.drop(columns=redundant_cols_existing)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 13)
        update_progress(13, 15, f"Redundant features removed ({len(redundant_cols_existing)} columns)", df.shape)

        # STEP 14: FINAL CLEANUP
        update_progress(14, 15, "Final cleanup...", None)
        rows_before = len(df)
        df = df.dropna()
        rows_dropped = rows_before - len(df)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 14)
        update_progress(14, 15, f"Final cleanup complete ({rows_dropped} rows removed)", df.shape)

        # STEP 15: SAVE PREPROCESSED DATA
        update_progress(15, 15, "Saving preprocessed data...", None)
        df.to_csv(OUTPUT_PATH, index=False)
        update_metrics(df.shape[0], df.shape[1], df.isnull().sum().sum(), 15)
        update_progress(15, 15, f"Data saved to {OUTPUT_PATH}", df.shape)

        # FINAL SUMMARY
        progress_bar.progress(1.0)
        status_text.markdown("### ✅ Preprocessing Complete!")
        
        st.markdown("---")
        st.success("🎉 Preprocessing pipeline completed successfully!")

        # Summary statistics
        st.markdown("### 📊 Final Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Initial Rows", f"{initial_shape[0]:,}")
            st.metric("Final Rows", f"{df.shape[0]:,}")
            st.metric("Rows Removed", f"{initial_shape[0] - df.shape[0]:,}", 
                      delta=f"-{((initial_shape[0] - df.shape[0])/initial_shape[0]*100):.1f}%")
        
        with col2:
            st.metric("Initial Columns", f"{initial_shape[1]}")
            st.metric("Final Columns", f"{df.shape[1]}")
            st.metric("Columns Changed", f"{initial_shape[1] - df.shape[1]}", 
                      delta=f"{df.shape[1] - initial_shape[1]:+d}")
        
        with col3:
            st.metric("Missing Values", "0", delta="100% clean")
            st.metric("Data Quality", "✓ Validated")
            st.metric("File Saved", "✓ Success")
        
        # Display sample data
        st.markdown("### 📋 Sample of Preprocessed Data")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Column information
        with st.expander("📑 Final Column List"):
            st.write(f"**Total Columns:** {len(df.columns)}")
            cols_str = ", ".join(df.columns)
            st.code(cols_str, language="text")
        
        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Preprocessed Data (CSV)",
            data=csv,
            file_name=OUTPUT_PATH.split("/")[-1],
            mime='text/csv',
            type="primary",
            use_container_width=True
        )
        
    except FileNotFoundError:
        st.error(f"❌ File not found: {DATA_PATH}")
        st.info("Please check the file path and make sure the file exists.")
    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        with st.expander("📋 Error Details"):
            st.exception(e)
