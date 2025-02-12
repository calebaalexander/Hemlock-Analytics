import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config
st.set_page_config(
    page_title="Pris Bar Analytics",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced Custom CSS with better card styling and hover effects
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
    .big-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .small-number {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 0.25rem;
    }
    .metric-title {
        font-size: 1rem;
        color: #444;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .trend-positive {
        color: #28a745;
    }
    .trend-negative {
        color: #dc3545;
    }
    .stApp {
        background-color: #fafafa;
    }
    </style>
""", unsafe_allow_html=True)

def load_sales_data():
    try:
        df = pd.read_excel('Hemlock2023.xlsx')
        # Enhanced data cleaning
        df = df[df['Order type'].isin(['Dine-in', 'Other'])]
        
        # Convert sales columns to numeric, handling any non-numeric values
        numeric_columns = ['Total sales', 'Covers', 'Receipts']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Add derived metrics
        df['revenue_per_cover'] = df['Total sales'] / df['Covers']
        df['average_check'] = df['Total sales'] / df['Receipts']
        
        return df
    except Exception as e:
        st.error(f"Error loading sales data: {str(e)}")
        return None

def analyze_sales_categories(df):
    """Analyze sales by category and return insights"""
    categories = {
        'COCKTAILS': df[df.index.str.contains('COCKTAILS', na=False)]['Total sales'].sum(),
        'BEER': df[df.index.str.contains('BEER', na=False)]['Total sales'].sum(),
        'FOOD': df[df.index.str.contains('FOOD', na=False)]['Total sales'].sum(),
        'SPIRITS': df[df.index.str.contains('SPIRITS', na=False)]['Total sales'].sum(),
        'WINE': df[df.index.str.contains('WINE', na=False)]['Total sales'].sum()
    }
    return pd.Series(categories)

def create_sales_trend_chart(df):
    """Create a sales trend visualization"""
    fig = go.Figure()
    
    # Add traces for different metrics
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Total sales'].rolling(7).mean(),
        name='7-day Average Sales',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig.update_layout(
        title="Sales Trend Analysis",
        xaxis_title="Date",
        yaxis_title="Sales ($)",
        hovermode='x unified',
        showlegend=True
    )
    return fig

def main():
    st.title("🍸 Pris Bar Performance Dashboard")

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

    df = load_sales_data()
    if df is not None:
        # Top-level metrics with enhanced styling
        st.subheader("Key Performance Metrics")
        
        metrics_cols = st.columns(4)
        with metrics_cols[0]:
            total_revenue = df['Total sales'].sum()
            prev_revenue = total_revenue * 0.9  # Example - replace with actual previous period
            revenue_growth = ((total_revenue - prev_revenue) / prev_revenue) * 100
            
            st.metric(
                "Total Revenue",
                f"${total_revenue:,.2f}",
                f"{revenue_growth:+.1f}% vs prev period",
                delta_color="normal"
            )

        with metrics_cols[1]:
            avg_check = total_revenue / df['Receipts'].sum()
            st.metric(
                "Average Check",
                f"${avg_check:.2f}",
                help="Average spend per order"
            )

        with metrics_cols[2]:
            covers = df['Covers'].sum()
            revenue_per_cover = total_revenue / covers
            st.metric(
                "Revenue per Cover",
                f"${revenue_per_cover:.2f}",
                f"{covers:,} total covers"
            )

        with metrics_cols[3]:
            total_items = df['Receipts'].sum()
            items_per_cover = total_items / covers
            st.metric(
                "Items per Cover",
                f"{items_per_cover:.1f}",
                f"{total_items:,} total items"
            )

        # Sales Analysis Section
        st.subheader("Sales Analysis")
        
        tabs = st.tabs(["Category Analysis", "Top Items", "Trends"])
        
        with tabs[0]:
            category_data = analyze_sales_categories(df)
            fig = px.pie(
                values=category_data.values,
                names=category_data.index,
                title="Sales Distribution by Category"
            )
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            # Top selling items analysis
            top_items = df.nlargest(10, 'Total sales')
            fig = px.bar(
                top_items,
                x=top_items.index,
                y='Total sales',
                title="Top 10 Items by Revenue"
            )
            st.plotly_chart(fig, use_container_width=True)

        with tabs[2]:
            # Sales trend analysis
            trend_chart = create_sales_trend_chart(df)
            st.plotly_chart(trend_chart, use_container_width=True)

        # Additional Insights
        st.subheader("Key Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Revenue Breakdown")
            st.markdown(f"""
            - Total Revenue: ${total_revenue:,.2f}
            - Average Check: ${avg_check:.2f}
            - Revenue per Cover: ${revenue_per_cover:.2f}
            """)

        with col2:
            st.markdown("#### Performance Metrics")
            st.markdown(f"""
            - Total Covers: {covers:,}
            - Total Items Sold: {total_items:,}
            - Items per Cover: {items_per_cover:.1f}
            """)

if __name__ == "__main__":
    main()
