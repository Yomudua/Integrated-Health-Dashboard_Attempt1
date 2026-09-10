import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# 1. Page Configuration & Layout
st.set_page_config(page_title="Clinical Analytics", page_icon="🏥", layout="wide")
st.title("🏥 Patient Health Analytics Dashboard")
st.markdown("---")

# 2. Securely connect to your free database using Streamlit Secrets
DB_USER = st.secrets["db_user"]
DB_PASSWORD = st.secrets["db_password"]
DB_HOST = st.secrets["db_host"]
DB_PORT = st.secrets["db_port"]
DB_NAME = st.secrets["db_name"]

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@st.cache_data(ttl=60)
def fetch_data():
    engine = create_engine(DATABASE_URL)
    # REPLACE 'patient_records' with your exact Supabase table name!
    return pd.read_sql("SELECT * FROM patient_records", engine)

try:
    df = fetch_data()
    
    # 🚨 DEBUG CHECK: If the database is empty, show a warning instead of a blank screen
    if df.empty:
        st.warning("⚠️ Database connected, but the table contains zero patient records.")
    else:
        # ==========================================
        # 📊 VISUALIZATION 1: High-Level KPI Blocks
        # ==========================================
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="👥 Total Patients", value=len(df))
        with col2:
            # Assumes you have an 'age' column (lowercase or uppercase)
            age_col = next((c for c in df.columns if c.lower() == 'age'), None)
            if age_col:
                st.metric(label="🎂 Avg Patient Age", value=f"{df[age_col].mean():.1f} Yrs")
        with col3:
            # Assumes you have a 'readmitted' column
            readmit_col = next((c for c in df.columns if c.lower() == 'readmitted'), None)
            if readmit_col:
                rate = (df[readmit_col].astype(int).sum() / len(df)) * 100
                st.metric(label="🔄 Readmission Rate", value=f"{rate:.1f}%")

        st.markdown("---")

        # ==========================================
        # 📈 VISUALIZATION 2: Side-by-Side Charts
        # ==========================================
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("💡 Patient Demographics")
            gender_col = next((c for c in df.columns if c.lower() == 'gender'), None)
            if gender_col:
                fig_pie = px.pie(df, names=gender_col, title="Gender Distribution Breakdown", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Missing a 'Gender' column to show this breakdown.")
                
        with chart_col2:
            st.subheader("📉 Clinical Vitals Trend")
            date_col = next((c for c in df.columns if c.lower() in ['date', 'admissiondate']), None)
            bp_col = next((c for c in df.columns if c.lower() in ['bp', 'bloodpressure', 'systolic']), None)
            
            if date_col and bp_col:
                fig_line = px.line(df, x=date_col, y=bp_col, title="Blood Pressure History over Time")
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("Ensure you have 'Date' and 'BloodPressure' columns to plot trends.")

        # ==========================================
        # 🔍 VISUALIZATION 3: Raw Interactive Table
        # ==========================================
        st.markdown("---")
        with st.expander("🔍 Inspect Full Patient Database Table"):
            st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"❌ Connection Error: Streamlit cannot talk to your database. Details: {e}")
