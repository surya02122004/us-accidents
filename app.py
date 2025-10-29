import streamlit as st
import sys
import os

# -----------------------------------------------------------
# 1️⃣ Page Configuration (ONLY ONCE and AT THE TOP)
# -----------------------------------------------------------
st.set_page_config(
    page_title="DV RoadSafe Analytics",
    page_icon="🚗",
    layout="wide"
)

# -----------------------------------------------------------
# 2️⃣ Hide default Streamlit multipage sidebar
# -----------------------------------------------------------
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# 3️⃣ Dynamic Module Import Setup
# -----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(BASE_DIR, "modules")
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

# -----------------------------------------------------------
# 4️⃣ Sidebar Navigation
# -----------------------------------------------------------
st.sidebar.title("🚦 DV RoadSafe Navigation")
st.sidebar.markdown("---")

section = st.sidebar.radio(
    "📍 Go to Section",
    [
        "🏠 Home Dashboard",
        "🧹 Preprocessing",
        "📊 Univariate Analysis",
        "📈 Comparative Analysis",
        "🗺️ Geospatial Analysis",
        "💡 Insights & Hypothesis",
        "✅ Key Findings"
    ],
    index=0
)

# -----------------------------------------------------------
# 5️⃣ Load Modules Based on Selection (With Error Handling)
# -----------------------------------------------------------
try:
    if section == "🏠 Home Dashboard":
        from Home import run
        run()

    elif section == "🧹 Preprocessing":
        from Preprocessing import run
        run()

    elif section == "📊 Univariate Analysis":
        from Univariate_Analysis import run
        run()

    elif section == "📈 Comparative Analysis":
        from Comparative_Analysis import run
        run()

    elif section == "🗺️ Geospatial Analysis":
        from Geospatial_Analysis import run
        run()

    elif section == "💡 Insights & Hypothesis":
        from Insights_and_Hypothesis import run
        run()

    elif section == "✅ Key Findings":
        from Key_Findings import run
        run()

except ImportError as e:
    st.error(f"❌ Module Import Error: {str(e)}")
    st.info(f"Make sure the file exists in the `modules/` folder")
    st.code(str(e), language="python")

except Exception as e:
    st.error(f"❌ Unexpected Error: {str(e)}")
    st.exception(e)

# -----------------------------------------------------------
# 6️⃣ Footer
# -----------------------------------------------------------
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #888; font-size: 12px; margin-top: 20px;">
        <p>🚗 <b>DV RoadSafe Analytics</b> | US Accidents Data Analysis & Preprocessing</p>
        <p>Built with Streamlit | Data Science Project</p>
    </div>
""", unsafe_allow_html=True)
