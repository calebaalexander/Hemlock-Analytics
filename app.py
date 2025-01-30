import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Hemlock Analytics", page_icon="🍸", layout="wide")

def load_data():
    try:
        # Read the Excel file and select the relevant sheet (if needed)
        df = pd.read_excel('Hemlock2023.xlsx', sheet_name=0)
        
        # Debug output
        st.write("DataFrame Info:")
        st.write(df.info())
        st.write("First few rows:")
        st.write(df.head())
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def main():
    st.title("🍸 Hemlock Bar Analytics Dashboard")
    
    # Authentication
    if 'authenticated' not in st.session_state:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Log In"):
                if username.lower() == "admin" and password == "Hemlock123":
                    st.session_state['authenticated'] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        return

    # Load and print raw data structure
    df = load_data()
    if df is not None:
        st.write("Available columns:", df.columns.tolist())
        
        # Display raw data table
        st.subheader("Raw Data")
        st.dataframe(df)

if __name__ == "__main__":
    main()
