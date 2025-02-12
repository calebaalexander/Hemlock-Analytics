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

def clean_numeric_data(df, column):
    """Clean numeric data by removing any non-numeric characters"""
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

def load_and_process_data():
    """Load and process data with accurate calculations"""
    try:
        df = pd.read_excel('Pine.xlsx', sheet_name='2023 Product Breakdown')
        
        # Clean numeric columns
        numeric_columns = [
            'Total Amount',
            'Total Quantity',
            'Total Transaction Count',
            'Margin',
            'Costs'
        ]
        
        for col in numeric_columns:
            df = clean_numeric_data(df, col)
        
        # Filter out rows with NaN values
        df = df.dropna(subset=['Total Amount', 'Total Quantity', 'Total Transaction Count'])
        
        # Calculate summary metrics
        summary = {
            'total_sales': df['Total Amount'].sum(),
            'total_quantity': df['Total Quantity'].sum(),
            'total_transactions': df['Total Transaction Count'].sum(),
            'total_costs': df['Costs'].sum() if 'Costs' in df.columns else 0,
            'total_margin': df['Margin'].sum() if 'Margin' in df.columns else 0
        }
        
        # Calculate derived metrics
        summary['avg_transaction'] = summary['total_sales'] / summary['total_transactions']
        summary['daily_average'] = summary['total_sales'] / 30  # Assuming 30 days
        summary['margin_percentage'] = (summary['total_margin'] / summary['total_sales'] * 100) if summary['total_sales'] > 0 else 0
        summary['revenue_per_item'] = summary['total_sales'] / summary['total_quantity']
        summary['items_per_transaction'] = summary['total_quantity'] / summary['total_transactions']
        
        return df, summary
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def format_currency(value):
    """Format currency values consistently"""
    return f"${value:,.2f}"

def main():
    st.title("🍸 Pris Bar Advanced Analytics Dashboard")

    df, summary = load_and_process_data()
    if df is None or summary is None:
        return

    # Key Performance Metrics
    st.header("Key Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Revenue",
            format_currency(summary['total_sales']),
            format_currency(summary['daily_average']) + "/day"
        )
    
    with col2:
        st.metric(
            "Average Transaction",
            format_currency(summary['avg_transaction']),
            f"{summary['total_transactions']:,.0f} transactions"
        )
    
    with col3:
        st.metric(
            "Total Margin",
            format_currency(summary['total_margin']),
            f"{summary['margin_percentage']:.1f}% margin"
        )
    
    with col4:
        st.metric(
            "Items Sold",
            f"{summary['total_quantity']:,.0f}",
            format_currency(summary['total_costs']) + " cost"
        )

    # Product Analysis
    st.header("Product Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 by revenue
        top_revenue = df.nlargest(10, 'Total Amount')
        fig_revenue = px.bar(
            top_revenue,
            x='SKU',
            y='Total Amount',
            title="Top 10 Products by Revenue"
        )
        fig_revenue.update_layout(
            xaxis_title="Product",
            yaxis_title="Revenue ($)",
            height=400
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Top 10 by margin
        top_margin = df.nlargest(10, 'Margin')
        fig_margin = px.bar(
            top_margin,
            x='SKU',
            y='Margin',
            title="Top 10 Products by Margin"
        )
        fig_margin.update_layout(
            xaxis_title="Product",
            yaxis_title="Margin ($)",
            height=400
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    # Sales Summary
    st.header("Sales Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Products")
        # Find top performers
        top_revenue_product = df.loc[df['Total Amount'].idxmax()]
        top_margin_product = df.loc[df['Margin'].idxmax()]
        top_transaction_product = df.loc[df['Total Transaction Count'].idxmax()]
        
        st.write(f"• Best selling product: {top_revenue_product['SKU']}")
        st.write(f"• Highest revenue: {format_currency(top_revenue_product['Total Amount'])}")
        st.write(f"• Best margin: {format_currency(top_margin_product['Margin'])}")
        st.write(f"• Most transactions: {int(top_transaction_product['Total Transaction Count']):,}")
    
    with col2:
        st.subheader("Efficiency Metrics")
        st.write(f"• Cost of Goods: {(summary['total_costs']/summary['total_sales']*100 if summary['total_sales']>0 else 0):.1f}%")
        st.write(f"• Margin per Transaction: {format_currency(summary['total_margin']/summary['total_transactions'])}")
        st.write(f"• Revenue per Item: {format_currency(summary['revenue_per_item'])}")
        st.write(f"• Average Items per Transaction: {summary['items_per_transaction']:.1f}")

if __name__ == "__main__":
    main()
