import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Pine Bar Analytics",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def calculate_net_metrics(row):
    """Calculate net metrics considering all transaction types"""
    # Net amount = Transaction Amount (already includes discounts) - Loss Amount - Returned Amount
    net_amount = (row['Transaction Amount'] or 0) - (row['Loss Amount'] or 0) - (row['Returned Amount'] or 0)
    
    # Net quantity = Transaction Quantity - Loss Quantity - Returned Quantity
    net_quantity = (row['Transaction Quantity'] or 0) - (row['Loss Quantity'] or 0) - (row['Returned Quantity'] or 0)
    
    # Net transactions = Transaction Count - Loss Transaction Count - Returned Transaction Count
    net_transactions = (row['Transaction Count'] or 0) - (row['Loss Transaction Count'] or 0) - (row['Returned Transaction Count'] or 0)
    
    return pd.Series({
        'Net Amount': net_amount,
        'Net Quantity': net_quantity,
        'Net Transactions': net_transactions
    })

def load_and_process_data():
    """Load and process data with proper handling of transaction types"""
    try:
        df = pd.read_excel('Pine.xlsx', sheet_name='2023 Product Breakdown')
        
        # Calculate net metrics
        net_metrics = df.apply(calculate_net_metrics, axis=1)
        df = pd.concat([df, net_metrics], axis=1)
        
        # Filter out categories (rows without SKUs) and remove rows with zero or negative net amounts
        product_df = df[df['SKU'].notna() & (df['Net Amount'] > 0)].copy()
        
        # Calculate category totals
        category_df = df[df['SKU'].isna()].copy()
        
        # Calculate summary metrics
        summary = {
            'total_net_sales': df['Net Amount'].sum(),
            'total_net_quantity': df['Net Quantity'].sum(),
            'total_net_transactions': df['Net Transactions'].sum(),
            'total_discounted_amount': abs(df['Discounted Amount'].sum()),
            'total_loss_amount': abs(df['Loss Amount'].sum())
        }
        
        # Calculate derived metrics
        summary['avg_transaction'] = (summary['total_net_sales'] / summary['total_net_transactions'] 
                                    if summary['total_net_transactions'] > 0 else 0)
        summary['daily_average'] = summary['total_net_sales'] / 365  # Annual average
        
        return product_df, category_df, summary
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def format_currency(value):
    """Format currency values with validation"""
    try:
        return f"${abs(float(value)):,.2f}"
    except:
        return "$0.00"

def create_bar_chart(df, x_col, y_col, title, color=None):
    """Create a consistent bar chart with improved formatting"""
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color=color,
        color_discrete_sequence=['#2E86C1'] if not color else None
    )
    fig.update_layout(
        xaxis_title="Product",
        yaxis_title=f"{y_col} ($)" if 'Amount' in y_col else y_col,
        height=400,
        xaxis_tickangle=-45,
        margin=dict(t=50, l=50, r=20, b=100)
    )
    return fig

def main():
    st.title("🍸 Pine Bar Advanced Analytics Dashboard")
    
    product_df, category_df, summary = load_and_process_data()
    if product_df is None or category_df is None or summary is None:
        return

    # Key Performance Metrics
    st.header("Key Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Net Revenue",
            format_currency(summary['total_net_sales']),
            f"{format_currency(summary['daily_average'])}/day"
        )
    
    with col2:
        st.metric(
            "Average Transaction",
            format_currency(summary['avg_transaction']),
            f"{summary['total_net_transactions']:,.0f} transactions"
        )
    
    with col3:
        st.metric(
            "Total Discounts",
            format_currency(summary['total_discounted_amount']),
            f"{(summary['total_discounted_amount']/summary['total_net_sales']*100):.1f}% of sales"
        )
    
    with col4:
        st.metric(
            "Items Sold (Net)",
            f"{summary['total_net_quantity']:,.0f}",
            f"{format_currency(summary['total_loss_amount'])} in losses"
        )

    # Category Analysis
    st.header("Category Performance")
    
    # Filter and sort categories
    category_totals = category_df[category_df['Net Amount'] > 0].sort_values('Net Amount', ascending=False)
    
    fig_categories = px.bar(
        category_totals,
        x=category_totals.index,
        y='Net Amount',
        title="Revenue by Category",
        color_discrete_sequence=['#2E86C1']
    )
    fig_categories.update_layout(
        xaxis_title="Category",
        yaxis_title="Net Revenue ($)",
        height=400
    )
    st.plotly_chart(fig_categories, use_container_width=True)

    # Product Analysis
    st.header("Top Products")
    col1, col2 = st.columns(2)
    
    with col1:
        top_revenue = product_df.nlargest(10, 'Net Amount')
        fig_revenue = create_bar_chart(
            top_revenue, 
            'SKU', 
            'Net Amount',
            "Top 10 Products by Revenue"
        )
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        top_quantity = product_df.nlargest(10, 'Net Quantity')
        fig_quantity = create_bar_chart(
            top_quantity,
            'SKU',
            'Net Quantity',
            "Top 10 Products by Quantity Sold"
        )
        st.plotly_chart(fig_quantity, use_container_width=True)

    # Transaction Analysis
    st.header("Transaction Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Performers")
        top_revenue_product = product_df.loc[product_df['Net Amount'].idxmax()]
        st.write(f"• Most Revenue: {top_revenue_product['SKU']}")
        st.write(f"  Revenue: {format_currency(top_revenue_product['Net Amount'])}")
        st.write(f"  Quantity: {int(top_revenue_product['Net Quantity']):,} units")
        
        top_transaction_product = product_df.loc[product_df['Net Transactions'].idxmax()]
        st.write(f"• Most Frequent: {top_transaction_product['SKU']}")
        st.write(f"  Transactions: {int(top_transaction_product['Net Transactions']):,}")
    
    with col2:
        st.subheader("Sales Metrics")
        st.write(f"• Average Transaction Value: {format_currency(summary['avg_transaction'])}")
        st.write(f"• Daily Revenue: {format_currency(summary['daily_average'])}")
        st.write(f"• Discount Rate: {(summary['total_discounted_amount']/summary['total_net_sales']*100):.1f}%")
        st.write(f"• Loss Rate: {(summary['total_loss_amount']/summary['total_net_sales']*100):.1f}%")

if __name__ == "__main__":
    main()
