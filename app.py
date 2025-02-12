import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Pris Bar Analytics",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="expanded"  # Changed to expanded to show debug options
)

# Custom CSS (keeping your existing styles)
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .debug-info {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #ffc107;
    }
    .calculation-breakdown {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

def validate_data(df):
    """Validate data and return any issues found"""
    issues = []
    
    # Check for required columns
    required_columns = ['Order type', 'Total sales', 'Covers', 'Receipts', 'USD/cover', 'USD/receipt']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        issues.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check for numeric data
    numeric_columns = ['Total sales', 'Covers', 'Receipts', 'USD/cover', 'USD/receipt']
    for col in numeric_columns:
        if col in df.columns:
            if not pd.to_numeric(df[col], errors='coerce').notna().all():
                issues.append(f"Non-numeric values found in {col}")
    
    # Check for negative values
    for col in numeric_columns:
        if col in df.columns:
            if (pd.to_numeric(df[col], errors='coerce') < 0).any():
                issues.append(f"Negative values found in {col}")
    
    # Check for missing values
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            issues.append(f"Missing values in {col}: {missing_count} rows")
    
    return issues

def calculate_metrics(df):
    """Calculate metrics with detailed breakdown"""
    metrics = {}
    breakdowns = {}
    
    try:
        # Total Sales
        metrics['total_sales'] = df['Total sales'].sum()
        breakdowns['total_sales'] = {
            'calculation': "Sum of 'Total sales' column",
            'by_order_type': df.groupby('Order type')['Total sales'].sum().to_dict()
        }
        
        # Covers
        metrics['total_covers'] = df['Covers'].sum()
        breakdowns['total_covers'] = {
            'calculation': "Sum of 'Covers' column",
            'by_order_type': df.groupby('Order type')['Covers'].sum().to_dict()
        }
        
        # Receipts
        metrics['total_receipts'] = df['Receipts'].sum()
        breakdowns['total_receipts'] = {
            'calculation': "Sum of 'Receipts' column",
            'by_order_type': df.groupby('Order type')['Receipts'].sum().to_dict()
        }
        
        # Average Check
        metrics['avg_check'] = metrics['total_sales'] / metrics['total_receipts']
        breakdowns['avg_check'] = {
            'calculation': f"Total Sales (${metrics['total_sales']:,.2f}) / Total Receipts ({metrics['total_receipts']:,})",
            'raw_calculation': f"{metrics['total_sales']} / {metrics['total_receipts']}"
        }
        
        # Revenue per Cover
        metrics['revenue_per_cover'] = metrics['total_sales'] / metrics['total_covers']
        breakdowns['revenue_per_cover'] = {
            'calculation': f"Total Sales (${metrics['total_sales']:,.2f}) / Total Covers ({metrics['total_covers']:,})",
            'raw_calculation': f"{metrics['total_sales']} / {metrics['total_covers']}"
        }
        
        # Items per Cover
        metrics['items_per_cover'] = metrics['total_receipts'] / metrics['total_covers']
        breakdowns['items_per_cover'] = {
            'calculation': f"Total Receipts ({metrics['total_receipts']:,}) / Total Covers ({metrics['total_covers']:,})",
            'raw_calculation': f"{metrics['total_receipts']} / {metrics['total_covers']}"
        }
        
    except Exception as e:
        st.error(f"Error in calculations: {str(e)}")
        return None, None
        
    return metrics, breakdowns

def load_sales_data():
    """Load and process sales data with validation"""
    try:
        df = pd.read_excel('Hemlock2023.xlsx')
        
        # Data validation
        issues = validate_data(df)
        if issues:
            st.warning("Data validation issues found:")
            for issue in issues:
                st.write(f"- {issue}")
        
        # Calculate metrics
        metrics, breakdowns = calculate_metrics(df)
        if metrics is None:
            return None, None, None
        
        return df, metrics, breakdowns
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def show_debug_info(df, metrics, breakdowns):
    """Display debug information and calculation breakdowns"""
    st.subheader("Debug Information")
    
    # Raw Data Sample
    with st.expander("Raw Data Sample"):
        st.dataframe(df.head())
        st.write("Data Types:", df.dtypes)
    
    # Calculation Breakdowns
    with st.expander("Calculation Breakdowns"):
        for metric, breakdown in breakdowns.items():
            st.markdown(f"### {metric}")
            st.markdown(f"**Formula:** {breakdown['calculation']}")
            if 'raw_calculation' in breakdown:
                st.markdown(f"**Raw calculation:** {breakdown['raw_calculation']}")
            if 'by_order_type' in breakdown:
                st.markdown("**Breakdown by Order Type:**")
                for order_type, value in breakdown['by_order_type'].items():
                    st.markdown(f"- {order_type}: {value:,.2f}")
    
    # Data Quality Metrics
    with st.expander("Data Quality Metrics"):
        st.markdown("### Missing Values")
        st.dataframe(df.isnull().sum())
        
        st.markdown("### Value Ranges")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        st.dataframe(df[numeric_cols].describe())

def main():
    st.title("🍸 Pris Bar Advanced Analytics Dashboard")

    # Add debug mode toggle in sidebar
    st.sidebar.title("Dashboard Settings")
    debug_mode = st.sidebar.checkbox("Enable Debug Mode")
    show_raw_data = st.sidebar.checkbox("Show Raw Data")
    show_calculations = st.sidebar.checkbox("Show Calculations")

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

    df, metrics, breakdowns = load_sales_data()
    if df is None or metrics is None:
        return

    # Main Dashboard
    tabs = st.tabs(["Overview", "Sales Analysis", "Category Analysis", "Debug View"])

    # Overview Tab
    with tabs[0]:
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${metrics['total_sales']:,.2f}",
                f"${metrics['total_sales']/30:,.2f}/day"
            )
            if show_calculations:
                st.markdown(breakdowns['total_sales']['calculation'])
        
        with col2:
            st.metric(
                "Average Check",
                f"${metrics['avg_check']:.2f}",
                f"{metrics['total_receipts']:,} receipts"
            )
            if show_calculations:
                st.markdown(breakdowns['avg_check']['calculation'])
        
        with col3:
            st.metric(
                "Revenue per Cover",
                f"${metrics['revenue_per_cover']:.2f}",
                f"{metrics['total_covers']:,} covers"
            )
            if show_calculations:
                st.markdown(breakdowns['revenue_per_cover']['calculation'])
        
        with col4:
            st.metric(
                "Items per Cover",
                f"{metrics['items_per_cover']:.1f}",
                f"{metrics['total_receipts']:,} items"
            )
            if show_calculations:
                st.markdown(breakdowns['items_per_cover']['calculation'])

    # Debug View Tab
    with tabs[3]:
        if debug_mode:
            show_debug_info(df, metrics, breakdowns)
        else:
            st.info("Enable Debug Mode in the sidebar to view detailed information")

    # Show raw data if enabled
    if show_raw_data:
        st.subheader("Raw Data")
        st.dataframe(df)

if __name__ == "__main__":
    main()
