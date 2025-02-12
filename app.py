import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Pris Bar Analytics",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_and_clean_data():
    """Load and clean the Excel data"""
    try:
        df = pd.read_excel('Hemlock2023.xlsx')
        
        # Clean numeric columns
        numeric_columns = ['Total sales', 'Covers', 'Receipts', 'USD/cover', 'USD/receipt']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Basic cleaning
        df = df[df['Order type'].notna()]
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def calculate_metrics(df):
    """Calculate key metrics and insights"""
    try:
        metrics = {
            'total_sales': df['Total sales'].sum(),
            'avg_check': df['Total sales'].sum() / df['Receipts'].sum(),
            'revenue_per_cover': df['Total sales'].sum() / df['Covers'].sum(),
            'items_per_cover': df['Receipts'].sum() / df['Covers'].sum(),
            'total_covers': df['Covers'].sum(),
            'total_receipts': df['Receipts'].sum()
        }
        
        # Time-based averages (using total sales divided by standard periods)
        metrics['daily_average'] = metrics['total_sales'] / 30  # Assuming 30 days
        metrics['monthly_average'] = metrics['total_sales']  # Already monthly data
        metrics['yearly_projection'] = metrics['monthly_average'] * 12
        
        return metrics
        
    except Exception as e:
        st.error(f"Error calculating metrics: {str(e)}")
        return None

def main():
    st.title("🍸 Pris Bar Advanced Analytics Dashboard")

    df = load_and_clean_data()
    if df is None:
        return

    metrics = calculate_metrics(df)
    if metrics is None:
        return

    # Key Metrics Section
    st.header("Key Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${metrics['total_sales']:,.2f}",
            f"${metrics['daily_average']:,.2f}/day"
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

    # Revenue Analysis Section
    st.header("Revenue Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Average Revenue")
        avg_metrics = {
            "Daily Average": f"${metrics['daily_average']:,.2f}",
            "Monthly Total": f"${metrics['monthly_average']:,.2f}",
            "Yearly Projection": f"${metrics['yearly_projection']:,.2f}"
        }
        
        for metric, value in avg_metrics.items():
            st.metric(metric, value)
    
    with col2:
        st.subheader("Key Insights")
        # Top performing items by revenue
        top_items = df.nlargest(5, 'Total sales')
        st.write("Top 5 Revenue Generators:")
        for idx, row in top_items.iterrows():
            st.write(f"• {row['Order type']}: ${row['Total sales']:,.2f}")

    # Sales Distribution
    st.header("Sales Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        order_type_data = df.groupby('Order type')['Total sales'].sum().nlargest(5)
        fig = px.pie(
            values=order_type_data.values,
            names=order_type_data.index,
            title="Top 5 Categories by Revenue"
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly trend (if date data is available)
        monthly_trend = px.bar(
            df.groupby('Order type')['Total sales'].sum().nlargest(5).reset_index(),
            x='Order type',
            y='Total sales',
            title="Top 5 Categories Revenue Breakdown"
        )
        monthly_trend.update_layout(xaxis_title="Category", yaxis_title="Revenue ($)")
        st.plotly_chart(monthly_trend, use_container_width=True)

    # Business Insights Section
    st.header("Business Insights")
    cols = st.columns(3)
    
    with cols[0]:
        st.subheader("Top Performers")
        st.write("Highest Revenue Day:")
        st.write("Most Popular Item:")
        st.write("Best Performing Category:")
    
    with cols[1]:
        st.subheader("Customer Behavior")
        st.write(f"Average Check Size: ${metrics['avg_check']:.2f}")
        st.write(f"Typical Items per Visit: {metrics['items_per_cover']:.1f}")
        st.write(f"Total Customer Visits: {metrics['total_covers']:,}")
    
    with cols[2]:
        st.subheader("Operational Metrics")
        st.write(f"Daily Revenue Target: ${metrics['daily_average']:,.2f}")
        st.write(f"Monthly Revenue Target: ${metrics['monthly_average']:,.2f}")
        st.write("Peak Hours: Coming soon")

if __name__ == "__main__":
    main()
