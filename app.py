import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import hashlib

# Page config
st.set_page_config(page_title="Hemlock Analytics", page_icon="🍸", layout="wide")

# Authentication
def check_password():
    def password_entered():
        if (st.session_state["username"].lower() == "admin" 
            and st.session_state["password"] == "Hemlock123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
            <style>
                .stTextInput > div > div > input {
                    width: 300px;
                }
            </style>""", unsafe_allow_html=True)
        
        st.title("🍸 Hemlock Bar Analytics")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown("### Login")
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.button("Log In", on_click=password_entered)
        return False
    
    elif not st.session_state["password_correct"]:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.error("😕 Invalid credentials")
        st.button("Log In", on_click=password_entered)
        return False
    else:
        return True

def load_data():
    try:
        # Read the Excel file
        df = pd.read_excel('Hemlock2023.xlsx')
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_summary_metrics(df):
    # Calculate key metrics
    total_sales = df['Total Amount'].sum()
    total_transactions = df['Total Transaction Count'].sum()
    avg_ticket = total_sales / total_transactions if total_transactions > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"${total_sales:,.2f}")
    with col2:
        st.metric("Total Transactions", f"{total_transactions:,}")
    with col3:
        st.metric("Average Ticket", f"${avg_ticket:.2f}")

def create_category_analysis(df):
    # Group by main categories
    categories = df.groupby('SKU').agg({
        'Total Amount': 'sum',
        'Total Transaction Count': 'sum'
    }).reset_index()
    
    # Sales by Category
    fig_sales = px.bar(categories.sort_values('Total Amount', ascending=True), 
                      y='SKU', x='Total Amount',
                      title='Sales by Category',
                      orientation='h',
                      labels={'Total Amount': 'Sales ($)', 'SKU': 'Category'},
                      color='Total Amount',
                      color_continuous_scale='Viridis')
    st.plotly_chart(fig_sales, use_container_width=True)
    
    # Transactions by Category
    fig_trans = px.bar(categories.sort_values('Total Transaction Count', ascending=True),
                      y='SKU', x='Total Transaction Count',
                      title='Transactions by Category',
                      orientation='h',
                      labels={'Total Transaction Count': 'Number of Transactions', 'SKU': 'Category'},
                      color='Total Transaction Count',
                      color_continuous_scale='Viridis')
    st.plotly_chart(fig_trans, use_container_width=True)

def main():
    st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            background-color: #f0f2f6;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("🍸 Hemlock Bar Analytics Dashboard")
    
    # Load data
    df = load_data()
    
    if df is not None:
        # Create tabs
        tabs = st.tabs(["Overview", "Sales Analysis", "Category Details", "Menu Performance"])
        
        # Overview Tab
        with tabs[0]:
            st.header("Business Overview")
            create_summary_metrics(df)
            create_category_analysis(df)
        
        # Sales Analysis Tab
        with tabs[1]:
            st.header("Sales Analysis")
            
            # Filters
            col1, col2 = st.columns([1, 3])
            with col1:
                st.subheader("Filters")
                selected_categories = st.multiselect("Categories", 
                                                   df['SKU'].unique(),
                                                   default=df['SKU'].unique())
            
            # Filtered data visualizations
            filtered_df = df[df['SKU'].isin(selected_categories)]
            fig = px.pie(filtered_df, 
                        values='Total Amount', 
                        names='SKU',
                        title='Sales Distribution by Category')
            st.plotly_chart(fig, use_container_width=True)
        
        # Category Details Tab
        with tabs[2]:
            st.header("Category Performance")
            selected_cat = st.selectbox("Select Category", df['SKU'].unique())
            cat_data = df[df['SKU'] == selected_cat]
            
            # Category metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Category Sales", 
                         f"${cat_data['Total Amount'].sum():,.2f}")
            with col2:
                st.metric("Category Transactions", 
                         f"{cat_data['Total Transaction Count'].sum():,}")
            with col3:
                avg_transaction = (cat_data['Total Amount'].sum() / 
                                 cat_data['Total Transaction Count'].sum() 
                                 if cat_data['Total Transaction Count'].sum() > 0 else 0)
                st.metric("Average Transaction", f"${avg_transaction:.2f}")
        
        # Menu Performance Tab
        with tabs[3]:
            st.header("Menu Performance")
            st.subheader("Top Items by Revenue")
            
            # Top items table
            top_items = df.nlargest(10, 'Total Amount')[
                ['SKU', 'Total Amount', 'Total Transaction Count']
            ].reset_index(drop=True)
            
            st.dataframe(top_items.style.format({
                'Total Amount': '${:,.2f}',
                'Total Transaction Count': '{:,}'
            }))

if check_password():
    main()
