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
    """Load and process the Pine Excel data with exact column names"""
    try:
        # Debug: Print available columns
        df = pd.read_excel('Pine.xlsx', sheet_name='2023 Product Breakdown')
        st.write("Available columns:", df.columns.tolist())
        
        # Convert numeric columns - using exact column names
        numeric_cols = [
            'Total Amount', 
            'Total Quantity',
            'Total Trans',
            'Costs',
            'Margin'
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                st.error(f"Missing column: {col}")
        
        # Calculate summary metrics
        summary = {
            'total_sales': df['Total Amount'].sum(),
            'total_quantity': df['Total Quantity'].sum(),
            'total_transactions': df['Total Trans'].sum(),
            'total_costs': df['Costs'].sum(),
            'total_margin': df['Margin'].sum()
        }
        
        return df, summary
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.write("Error details:", type(e).__name__, str(e))
        return None, None

def main():
    st.title("🍸 Pris Bar Advanced Analytics Dashboard")

    # Load data with debug info
    df, summary = load_and_process_data()
    if df is None or summary is None:
        return

    # Key Performance Metrics
    st.header("Key Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            f"${summary['total_sales']:,.2f}",
            f"${summary['total_sales']/30:,.2f}/day"
        )
    
    with col2:
        st.metric(
            "Average Transaction",
            f"${summary['total_sales']/summary['total_transactions']:.2f}",
            f"{summary['total_transactions']:,} transactions"
        )
    
    with col3:
        st.metric(
            "Total Margin",
            f"${summary['total_margin']:,.2f}",
            f"{(summary['total_margin']/summary['total_sales']*100):.1f}% margin"
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

    # Sales Summary
    st.header("Sales Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Products")
        top_seller = df.loc[df['Total Amount'].idxmax()]
        st.write(f"• Best selling product: {top_seller['SKU']}")
        st.write(f"• Highest revenue: ${top_seller['Total Amount']:,.2f}")
        st.write(f"• Best margin: ${df['Margin'].max():,.2f}")
        st.write(f"• Most transactions: {df['Total Trans'].max():,}")
    
    with col2:
        st.subheader("Efficiency Metrics")
        st.write(f"• Cost of Goods: {(summary['total_costs']/summary['total_sales']*100):.1f}%")
        st.write(f"• Margin per Transaction: ${summary['total_margin']/summary['total_transactions']:.2f}")
        st.write(f"• Revenue per Item: ${summary['total_sales']/summary['total_quantity']:.2f}")
        st.write(f"• Average Items per Transaction: {summary['total_quantity']/summary['total_transactions']:.1f}")

if __name__ == "__main__":
    main()
