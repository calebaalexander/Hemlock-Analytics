import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Pris Bar Analytics",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def load_and_process_data():
    """Load and process the Pine Excel data with correct column names"""
    try:
        # Read the Excel file
        df = pd.read_excel('Pine.xlsx', sheet_name='2023 Product Breakdown')
        
        # Convert columns to numeric - using exact column names from Excel
        numeric_cols = ['Total Amount', 'Total Quanti', 'Total Trans', 'Margin', 'Costs']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate summary metrics
        summary = {
            'total_sales': df['Total Amount'].sum(),
            'total_quantity': df['Total Quanti'].sum(),
            'total_transactions': df['Total Trans'].sum(),
            'total_costs': df['Costs'].sum(),
            'total_margin': df['Margin'].sum()
        }
        
        return df, summary
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def main():
    st.title("🍸 Pris Bar Advanced Analytics Dashboard")

    # Load data
    df, summary = load_and_process_data()
    if df is None or summary is None:
        return

    # Calculate key metrics
    daily_average = summary['total_sales'] / 30  # Assuming 30 days per month
    avg_transaction = summary['total_sales'] / summary['total_transactions']
    margin_percentage = (summary['total_margin'] / summary['total_sales']) * 100

    # Key Performance Metrics
    st.header("Key Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${summary['total_sales']:,.2f}",
            f"${daily_average:,.2f}/day"
        )
    
    with col2:
        st.metric(
            "Average Transaction",
            f"${avg_transaction:.2f}",
            f"{summary['total_transactions']:,} transactions"
        )
    
    with col3:
        st.metric(
            "Total Margin",
            f"${summary['total_margin']:,.2f}",
            f"{margin_percentage:.1f}% margin"
        )
    
    with col4:
        st.metric(
            "Items Sold",
            f"{summary['total_quantity']:,}",
            f"${summary['total_costs']:,.2f} cost"
        )

    # Product Analysis
    st.header("Product Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 products by revenue
        top_products = df.nlargest(10, 'Total Amount')
        fig_revenue = px.bar(
            top_products,
            x='SKU',
            y='Total Amount',
            title="Top 10 Products by Revenue"
        )
        fig_revenue.update_layout(xaxis_title="Product", yaxis_title="Revenue ($)")
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Top 10 products by margin
        top_margin = df.nlargest(10, 'Margin')
        fig_margin = px.bar(
            top_margin,
            x='SKU',
            y='Margin',
            title="Top 10 Products by Margin"
        )
        fig_margin.update_layout(xaxis_title="Product", yaxis_title="Margin ($)")
        st.plotly_chart(fig_margin, use_container_width=True)

    # Key Insights
    st.header("Key Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Performers")
        top_performer = df.loc[df['Total Amount'].idxmax()]
        st.write(f"• Best selling product: {top_performer['SKU']}")
        st.write(f"• Highest revenue: ${top_performer['Total Amount']:,.2f}")
        st.write(f"• Best margin: ${df['Margin'].max():,.2f}")
        st.write(f"• Most transactions: {df['Total Trans'].max():,}")
    
    with col2:
        st.subheader("Sales Summary")
        st.write(f"• Daily average sales: ${daily_average:,.2f}")
        st.write(f"• Average transaction value: ${avg_transaction:.2f}")
        st.write(f"• Total items sold: {summary['total_quantity']:,}")
        st.write(f"• Total cost of goods: ${summary['total_costs']:,.2f}")

    # Efficiency Metrics
    st.header("Efficiency Metrics")
    cols = st.columns(3)
    
    with cols[0]:
        st.metric(
            "Cost of Goods %",
            f"{(summary['total_costs'] / summary['total_sales'] * 100):.1f}%"
        )
    
    with cols[1]:
        st.metric(
            "Margin per Transaction",
            f"${summary['total_margin'] / summary['total_transactions']:.2f}"
        )
    
    with cols[2]:
        st.metric(
            "Revenue per Item",
            f"${summary['total_sales'] / summary['total_quantity']:.2f}"
        )

if __name__ == "__main__":
    main()
