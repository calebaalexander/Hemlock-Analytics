import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from collections import defaultdict

st.set_page_config(
    page_title="Pris Bar Analytics",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
    .trend-positive { color: #28a745; }
    .trend-negative { color: #dc3545; }
    .stApp { background-color: #fafafa; }
    </style>
""", unsafe_allow_html=True)

def load_sales_data():
    try:
        df = pd.read_excel('Hemlock2023.xlsx')
        df = df[df['Order type'].notna()]
        
        numeric_cols = ['Total sales', 'Covers', 'Receipts', 'Total Amount', 'Costs', 'Margin']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        summary = {
            'total_sales': df['Total Amount'].sum(),
            'total_covers': df['Covers'].sum(),
            'total_receipts': df['Receipts'].sum(),
            'avg_check': df['Total Amount'].sum() / df['Receipts'].sum(),
            'revenue_per_cover': df['Total Amount'].sum() / df['Covers'].sum()
        }
        
        return df, summary
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def analyze_cocktails(df):
    cocktail_data = df[df['SKU'].notna()]
    
    top_cocktails = cocktail_data.nlargest(10, 'Total Amount')[
        ['SKU', 'Total Amount', 'Total Quantity', 'Margin']
    ]
    
    margin_data = pd.DataFrame({
        'SKU': cocktail_data['SKU'],
        'Margin': cocktail_data['Margin'],
        'Cost': cocktail_data['Costs'],
        'Revenue': cocktail_data['Total Amount']
    })
    
    return top_cocktails, margin_data

def analyze_categories():
    categories = {
        'COCKTAILS': 167011.65,
        'BEER': 15967.45,
        'FOOD': 58645.45,
        'SPIRITS': 21143.45,
        'WINE': 13586.80,
        'N/A': 3836.40,
        'Merch': 553.80,
        'Misc': 439.00
    }
    return categories

def create_category_charts(categories):
    fig_pie = px.pie(
        values=list(categories.values()),
        names=list(categories.keys()),
        title="Revenue Distribution by Category"
    )
    
    fig_bar = px.bar(
        x=list(categories.keys()),
        y=list(categories.values()),
        title="Revenue by Category"
    )
    
    return fig_pie, fig_bar

def analyze_inventory(df):
    inventory = df.groupby('SKU').agg({
        'Total Quantity': 'sum',
        'Costs': 'sum',
        'Total Amount': 'sum',
        'Margin': 'mean'
    }).reset_index()
    
    inventory['Margin_Percentage'] = (inventory['Total Amount'] - inventory['Costs']) / inventory['Total Amount'] * 100
    
    return inventory

def main():
    st.title("🍸 Pris Bar Advanced Analytics Dashboard")

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

    df, summary = load_sales_data()
    if df is None or summary is None:
        return

    tabs = st.tabs(["Overview", "Cocktails", "Categories", "Inventory"])

    with tabs[0]:
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${summary['total_sales']:,.2f}",
                f"${summary['total_sales']/30:,.2f}/day"
            )
        
        with col2:
            st.metric(
                "Average Check",
                f"${summary['avg_check']:.2f}",
                f"{summary['total_receipts']:,} receipts"
            )
        
        with col3:
            st.metric(
                "Revenue per Cover",
                f"${summary['revenue_per_cover']:.2f}",
                f"{summary['total_covers']:,} covers"
            )
        
        with col4:
            items_per_cover = summary['total_receipts'] / summary['total_covers']
            st.metric(
                "Items per Cover",
                f"{items_per_cover:.1f}",
                f"{summary['total_receipts']:,} items"
            )

    with tabs[1]:
        st.subheader("Cocktail Analysis")
        top_cocktails, margin_data = analyze_cocktails(df)
        
        fig_top = px.bar(
            top_cocktails,
            x='SKU',
            y='Total Amount',
            title="Top 10 Cocktails by Revenue"
        )
        st.plotly_chart(fig_top, use_container_width=True)
        
        fig_margin = px.scatter(
            margin_data,
            x='Revenue',
            y='Margin',
            hover_data=['SKU'],
            title="Cocktail Margin Analysis"
        )
        st.plotly_chart(fig_margin, use_container_width=True)

    with tabs[2]:
        st.subheader("Category Analysis")
        categories = analyze_categories()
        fig_pie, fig_bar = create_category_charts(categories)
        
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.plotly_chart(fig_bar, use_container_width=True)

    with tabs[3]:
        st.subheader("Inventory Analysis")
        inventory = analyze_inventory(df)
        
        fig_inventory = px.scatter(
            inventory,
            x='Total Quantity',
            y='Margin_Percentage',
            hover_data=['SKU', 'Total Amount'],
            title="Product Movement vs Margin"
        )
        st.plotly_chart(fig_inventory, use_container_width=True)
        
        st.dataframe(
            inventory.sort_values('Total Amount', ascending=False)
            .head(10)
            .style.format({
                'Total Amount': '${:,.2f}',
                'Costs': '${:,.2f}',
                'Margin_Percentage': '{:.1f}%'
            })
        )

if __name__ == "__main__":
    main()
