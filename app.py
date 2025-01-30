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
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image("https://via.placeholder.com/150x150.png?text=H", width=100)
            st.markdown("#")
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
    # Sample data structure based on your Excel file
    data = {
        'category': ['BEER', 'COCKTAILS', 'FOOD', 'SPIRITS', 'WINE', 'MERCH', 'MISC', 'N/A'],
        'sales': [15967.45, 167011.65, 58645.45, 21143.45, 13586.80, 553.80, 439.00, 3836.40],
        'transactions': [2608, 15579, 9864, 2286, 1590, 55, 42, 610]
    }
    return pd.DataFrame(data)

def create_summary_metrics(data):
    total_sales = data['sales'].sum()
    total_transactions = data['transactions'].sum()
    avg_ticket = total_sales / total_transactions
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sales", f"${total_sales:,.2f}")
    with col2:
        st.metric("Total Transactions", f"{total_transactions:,}")
    with col3:
        st.metric("Average Ticket", f"${avg_ticket:.2f}")

def create_category_analysis(data):
    # Sales by Category
    fig_sales = px.bar(data, x='category', y='sales',
                      title='Sales by Category',
                      labels={'sales': 'Sales ($)', 'category': 'Category'},
                      color_discrete_sequence=['#2E86C1'])
    st.plotly_chart(fig_sales, use_container_width=True)
    
    # Transactions by Category
    fig_trans = px.bar(data, x='category', y='transactions',
                      title='Transactions by Category',
                      labels={'transactions': 'Number of Transactions', 'category': 'Category'},
                      color_discrete_sequence=['#28B463'])
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
        .reportview-container {
            margin-top: -2em;
        }
        .reportview-container .main .block-container {
            padding-top: 1em;
        }
        </style>
        """, unsafe_allow_html=True)

    st.title("🍸 Hemlock Bar Analytics Dashboard")
    
    # Load data
    data = load_data()
    
    # Create tabs
    tabs = st.tabs(["Overview", "Sales Analysis", "Category Details", "Staff & Operations"])
    
    # Overview Tab
    with tabs[0]:
        st.header("Business Overview")
        create_summary_metrics(data)
        create_category_analysis(data)
    
    # Sales Analysis Tab
    with tabs[1]:
        st.header("Sales Analysis")
        
        # Filters
        col1, col2 = st.columns([1, 3])
        with col1:
            st.subheader("Filters")
            selected_categories = st.multiselect("Categories", data['category'].unique(),
                                               default=data['category'].unique())
            
        # Filtered data visualizations
        filtered_data = data[data['category'].isin(selected_categories)]
        fig = px.pie(filtered_data, values='sales', names='category',
                    title='Sales Distribution by Category')
        st.plotly_chart(fig, use_container_width=True)
    
    # Category Details Tab
    with tabs[2]:
        st.header("Category Performance")
        selected_cat = st.selectbox("Select Category", data['category'].unique())
        cat_data = data[data['category'] == selected_cat]
        
        # Category metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Category Sales", f"${cat_data['sales'].iloc[0]:,.2f}")
        with col2:
            st.metric("Category Transactions", f"{cat_data['transactions'].iloc[0]:,}")
    
    # Staff & Operations Tab
    with tabs[3]:
        st.header("Staff & Operations")
        st.info("This section will include staff performance metrics, scheduling analytics, and operational insights once integrated with your staff management system.")

if check_password():
    main()
