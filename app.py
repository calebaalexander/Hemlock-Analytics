import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Pris Bar Analytics",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="expanded"
)

def clean_numeric_column(df, column):
    """Clean numeric columns by removing currency symbols and converting to float"""
    if column in df.columns:
        df[column] = df[column].apply(lambda x: str(x).replace('$', '').replace(',', '') if pd.notnull(x) else x)
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

def load_and_clean_data():
    """Load and clean the Excel data"""
    try:
        # Read the Excel file
        df = pd.read_excel('Hemlock2023.xlsx')
        
        # Store original row count
        original_rows = len(df)
        
        # Clean numeric columns
        numeric_columns = ['Total sales', 'Covers', 'Receipts', 'USD/cover', 'USD/receipt']
        for col in numeric_columns:
            df = clean_numeric_column(df, col)
        
        # Remove rows where all numeric columns are NaN
        df = df.dropna(subset=numeric_columns, how='all')
        
        # Remove summary rows and keep only meaningful data
        df = df[df['Order type'].notna()]
        
        # Log cleaning results
        st.sidebar.markdown("### Data Cleaning Report")
        st.sidebar.markdown(f"Original rows: {original_rows}")
        st.sidebar.markdown(f"Cleaned rows: {len(df)}")
        st.sidebar.markdown(f"Rows removed: {original_rows - len(df)}")
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def calculate_metrics(df):
    """Calculate key metrics from cleaned data"""
    try:
        # Filter out negative values for calculations
        calc_df = df[df['Total sales'] >= 0]
        
        metrics = {
            'total_sales': calc_df['Total sales'].sum(),
            'total_covers': calc_df['Covers'].sum(),
            'total_receipts': calc_df['Receipts'].sum()
        }
        
        # Calculate derived metrics
        if metrics['total_receipts'] > 0:
            metrics['avg_check'] = metrics['total_sales'] / metrics['total_receipts']
        else:
            metrics['avg_check'] = 0
            
        if metrics['total_covers'] > 0:
            metrics['revenue_per_cover'] = metrics['total_sales'] / metrics['total_covers']
            metrics['items_per_cover'] = metrics['total_receipts'] / metrics['total_covers']
        else:
            metrics['revenue_per_cover'] = 0
            metrics['items_per_cover'] = 0
            
        return metrics
        
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")
        return None

def main():
    st.title("🍸 Pris Bar Advanced Analytics Dashboard")
    
    # Sidebar controls
    st.sidebar.title("Dashboard Settings")
    show_raw_data = st.sidebar.checkbox("Show Raw Data")
    show_data_quality = st.sidebar.checkbox("Show Data Quality Metrics")

    # Load and clean data
    df = load_and_clean_data()
    if df is None:
        st.error("Failed to load data. Please check the Excel file.")
        return

    # Calculate metrics
    metrics = calculate_metrics(df)
    if metrics is None:
        st.error("Failed to calculate metrics.")
        return

    # Display data quality information if enabled
    if show_data_quality:
        st.subheader("Data Quality Metrics")
        
        # Missing values summary
        missing_data = df.isnull().sum()
        st.write("Missing Values by Column:")
        st.dataframe(missing_data[missing_data > 0])
        
        # Numeric columns statistics
        numeric_stats = df.describe()
        st.write("Numeric Columns Statistics:")
        st.dataframe(numeric_stats)

    # Display raw data if enabled
    if show_raw_data:
        st.subheader("Raw Data")
        st.dataframe(df)

    # Main metrics display
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${metrics['total_sales']:,.2f}",
            f"${metrics['total_sales']/30:,.2f}/day"
        )
    
    with col2:
        st.metric(
            "Average Check",
            f"${metrics['avg_check']:.2f}",
            f"{metrics['total_receipts']:,} receipts"
        )
    
    with col3:
        st.metric(
            "Revenue per Cover",
            f"${metrics['revenue_per_cover']:.2f}",
            f"{metrics['total_covers']:,} covers"
        )
    
    with col4:
        st.metric(
            "Items per Cover",
            f"{metrics['items_per_cover']:.1f}",
            f"{metrics['total_receipts']:,} items"
        )

    # Category analysis (if data is available)
    if 'Order type' in df.columns:
        st.subheader("Sales by Order Type")
        order_type_data = df.groupby('Order type')['Total sales'].sum().reset_index()
        fig = px.bar(
            order_type_data,
            x='Order type',
            y='Total sales',
            title="Sales by Order Type"
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
