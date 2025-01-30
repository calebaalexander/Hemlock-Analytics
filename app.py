import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Hemlock Analytics", page_icon="🍸", layout="wide")

def load_data():
    try:
        df = pd.read_excel('Hemlock2023.xlsx')
        # Convert 'Total sales' and percentages to numeric, removing any currency symbols
        df['Total sales'] = pd.to_numeric(df['Total sales'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_metrics(df):
    # Calculate total sales and other metrics
    total_sales = df['Total sales'].sum()
    total_receipts = df['Receipts'].sum()
    avg_receipt = total_sales / total_receipts if total_receipts > 0 else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"${total_sales:,.2f}")
    with col2:
        st.metric("Total Receipts", f"{total_receipts:,}")
    with col3:
        st.metric("Average Receipt", f"${avg_receipt:.2f}")

def create_sales_chart(df):
    # Create a bar chart of sales by order type
    fig = px.bar(df, 
                 x='Order type', 
                 y='Total sales',
                 title='Sales by Order Type',
                 labels={'Total sales': 'Sales ($)', 'Order type': 'Type'})
    fig.update_traces(marker_color='rgb(55, 83, 109)')
    st.plotly_chart(fig, use_container_width=True)

def create_receipts_chart(df):
    # Create a pie chart showing receipt distribution
    fig = px.pie(df, 
                 values='Receipts',
                 names='Order type',
                 title='Receipt Distribution by Order Type')
    st.plotly_chart(fig, use_container_width=True)

def main():
    # Authentication
    if 'authenticated' not in st.session_state:
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
    
    # Main dashboard
    st.title("🍸 Hemlock Bar Analytics Dashboard")
    
    df = load_data()
    if df is not None:
        tabs = st.tabs(["Sales Overview", "Order Analysis"])
        
        with tabs[0]:
            st.header("Sales Overview")
            create_metrics(df)
            
            # Display KPIs
            st.subheader("Key Performance Indicators")
            kpi_cols = st.columns(2)
            
            with kpi_cols[0]:
                st.metric("Average USD/Cover", 
                         f"${df['USD/cover'].mean():.2f}")
            with kpi_cols[1]:
                st.metric("Average USD/Receipt", 
                         f"${df['USD/receipt'].mean():.2f}")
            
            create_sales_chart(df)
        
        with tabs[1]:
            st.header("Order Analysis")
            
            # Filter by order type
            order_type = st.selectbox("Select Order Type", 
                                    df['Order type'].unique())
            
            filtered_df = df[df['Order type'] == order_type]
            
            # Display detailed metrics
            st.subheader(f"Details for {order_type}")
            detail_cols = st.columns(3)
            
            with detail_cols[0]:
                st.metric("Sales", 
                         f"${filtered_df['Total sales'].iloc[0]:,.2f}")
            with detail_cols[1]:
                st.metric("Covers", 
                         f"{filtered_df['Covers'].iloc[0]:,}")
            with detail_cols[2]:
                st.metric("Receipts",
                         f"{filtered_df['Receipts'].iloc[0]:,}")
            
            # Display data table
            st.subheader("Detailed Data")
            st.dataframe(filtered_df[[
                'Order type', 'Total sales', 'Covers', 
                'Receipts', 'USD/cover', 'USD/receipt'
            ]].style.format({
                'Total sales': '${:,.2f}',
                'USD/cover': '${:,.2f}',
                'USD/receipt': '${:,.2f}'
            }))

if __name__ == "__main__":
    main()
