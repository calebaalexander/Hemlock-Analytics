import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Hemlock Analytics", page_icon="🍸", layout="wide")

def load_data():
    try:
        # Read the Excel file
        df = pd.read_excel('Hemlock2023.xlsx')
        # Print columns for debugging
        st.write("Available columns:", list(df.columns))
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def main():
    st.title("🍸 Hemlock Bar Analytics Dashboard")
    
    # Check authentication
    if 'authenticated' not in st.session_state:
        # Login form
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
    
    # Load and display data
    df = load_data()
    
    if df is not None:
        # Create tabs for different views
        tab1, tab2 = st.tabs(["Sales Overview", "Category Analysis"])
        
        with tab1:
            st.header("Sales Overview")
            
            # Display raw data for debugging
            st.subheader("Raw Data Preview")
            st.dataframe(df.head())
            
            # Display column information
            st.subheader("Column Information")
            st.write(df.info())
            
            try:
                # Summary metrics
                sales_col = [col for col in df.columns if 'amount' in col.lower() or 'sales' in col.lower()]
                trans_col = [col for col in df.columns if 'transaction' in col.lower()]
                
                if sales_col and trans_col:
                    total_sales = df[sales_col[0]].sum()
                    total_transactions = df[trans_col[0]].sum()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Sales", f"${total_sales:,.2f}")
                    with col2:
                        st.metric("Total Transactions", f"{total_transactions:,}")
            except Exception as e:
                st.error(f"Error calculating metrics: {str(e)}")
        
        with tab2:
            st.header("Category Analysis")
            
            try:
                # Category selector
                if 'SKU' in df.columns:
                    selected_category = st.selectbox(
                        "Select Category",
                        options=sorted(df['SKU'].unique())
                    )
                    
                    if selected_category:
                        cat_data = df[df['SKU'] == selected_category]
                        st.write(f"Data for {selected_category}:")
                        st.dataframe(cat_data)
                else:
                    st.warning("Category column (SKU) not found in the data")
            except Exception as e:
                st.error(f"Error in category analysis: {str(e)}")

if __name__ == "__main__":
    main()
