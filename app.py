import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Pine Bar Analytics", page_icon="🍸", layout="wide")

def clean_numeric_data(df, column):
    """Clean numeric data by removing any non-numeric characters"""
    if column in df.columns:
        df[column] = pd.to_numeric(df[column].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')
    return df

def load_and_process_data():
    """Load and process data with proper category handling"""
    try:
        # Read the Excel file
        df = pd.read_excel('Pine.xlsx', sheet_name='2023 Product Breakdown')
        
        # Clean numeric columns
        numeric_columns = [
            'Transaction Amount', 'Total Quantity', 'Transaction Count',
            'Loss Amount', 'Loss Quantity', 'Loss Transaction Count',
            'Returned Amount', 'Returned Quantity', 'Returned Transaction Count',
            'Discounted Amount', 'Discounted Quantity', 'Discounted Transaction Count'
        ]
        
        for col in numeric_columns:
            df = clean_numeric_data(df, col)
        
        # Calculate net metrics
        df['Net Amount'] = (df['Transaction Amount'].fillna(0) - 
                          df['Loss Amount'].fillna(0) - 
                          df['Returned Amount'].fillna(0))
        
        df['Net Quantity'] = (df['Transaction Quantity'].fillna(0) - 
                           df['Loss Quantity'].fillna(0) - 
                           df['Returned Quantity'].fillna(0))
        
        df['Net Transactions'] = (df['Transaction Count'].fillna(0) - 
                               df['Loss Transaction Count'].fillna(0) - 
                               df['Returned Transaction Count'].fillna(0))
        
        # Get main categories
        categories_df = df[
            (df['SKU'].isna()) & 
            (df['Transaction Amount'].notna()) &
            (df['Transaction Amount'] != 0)
        ].copy()
        
        # Get products
        products_df = df[
            df['SKU'].notna() & 
            (df['Net Amount'] > 0)
        ].copy()
        
        # Calculate summary metrics
        summary = {
            'total_net_sales': products_df['Net Amount'].sum(),
            'total_net_quantity': products_df['Net Quantity'].sum(),
            'total_net_transactions': products_df['Net Transactions'].sum(),
            'total_discounted_amount': abs(df['Discounted Amount'].fillna(0).sum()),
            'total_loss_amount': abs(df['Loss Amount'].fillna(0).sum())
        }
        
        return categories_df, products_df, summary
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def main():
    st.title("🍸 Pine Bar Advanced Analytics Dashboard")
    
    categories_df, products_df, summary = load_and_process_data()
    if categories_df is None:
        return

    # Key Performance Metrics
    st.header("Key Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Net Revenue",
            f"${summary['total_net_sales']:,.2f}",
            f"${summary['total_net_sales']/365:,.2f}/day"
        )
    
    with col2:
        avg_transaction = summary['total_net_sales']/summary['total_net_transactions'] if summary['total_net_transactions'] > 0 else 0
        st.metric(
            "Average Transaction",
            f"${avg_transaction:,.2f}",
            f"{summary['total_net_transactions']:,.0f} transactions"
        )
    
    with col3:
        discount_rate = (summary['total_discounted_amount']/summary['total_net_sales']*100) if summary['total_net_sales'] > 0 else 0
        st.metric(
            "Total Discounts",
            f"${summary['total_discounted_amount']:,.2f}",
            f"{discount_rate:.1f}% of sales"
        )
    
    with col4:
        st.metric(
            "Items Sold (Net)",
            f"{summary['total_net_quantity']:,.0f}",
            f"${summary['total_loss_amount']:,.2f} in losses"
        )

    # Category Performance
    st.header("Category Performance")
    
    # Create category bar chart with sorted values
    categories_sorted = categories_df.sort_values('Net Amount', ascending=True)
    
    fig_categories = go.Figure(data=[
        go.Bar(
            x=categories_sorted['Net Amount'],
            y=categories_sorted.index,
            orientation='h',
            text=categories_sorted['Net Amount'].apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
            marker_color='#2E86C1'
        )
    ])
    
    fig_categories.update_layout(
        title={
            'text': "Revenue by Category",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Net Revenue ($)",
        yaxis_title="",
        height=400,
        showlegend=False,
        margin=dict(t=50, l=200, r=20, b=50)
    )
    
    st.plotly_chart(fig_categories, use_container_width=True)

    # Top Products Analysis
    st.header("Top Products")
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 by revenue
        top_revenue = products_df.nlargest(10, 'Net Amount')
        fig_revenue = go.Figure(data=[
            go.Bar(
                x=top_revenue['Net Amount'],
                y=top_revenue.index,
                orientation='h',
                text=top_revenue['Net Amount'].apply(lambda x: f'${x:,.0f}'),
                textposition='auto',
                marker_color='#2E86C1'
            )
        ])
        
        fig_revenue.update_layout(
            title={
                'text': "Top 10 Products by Revenue",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Net Revenue ($)",
            yaxis_title="",
            height=400,
            showlegend=False,
            margin=dict(t=50, l=200, r=20, b=50)
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        # Top 10 by quantity
        top_quantity = products_df.nlargest(10, 'Net Quantity')
        fig_quantity = go.Figure(data=[
            go.Bar(
                x=top_quantity['Net Quantity'],
                y=top_quantity.index,
                orientation='h',
                text=top_quantity['Net Quantity'].apply(lambda x: f'{x:,.0f}'),
                textposition='auto',
                marker_color='#2E86C1'
            )
        ])
        
        fig_quantity.update_layout(
            title={
                'text': "Top 10 Products by Quantity",
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Quantity Sold",
            yaxis_title="",
            height=400,
            showlegend=False,
            margin=dict(t=50, l=200, r=20, b=50)
        )
        
        st.plotly_chart(fig_quantity, use_container_width=True)

    # Transaction Analysis
    st.header("Transaction Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Performers")
        if not products_df.empty:
            top_product = products_df.loc[products_df['Net Amount'].idxmax()]
            st.write(f"• Most Revenue: {top_product.name}")
            st.write(f"  Revenue: ${top_product['Net Amount']:,.2f}")
            st.write(f"  Quantity: {int(top_product['Net Quantity']):,} units")
            
            most_frequent = products_df.loc[products_df['Net Transactions'].idxmax()]
            st.write(f"• Most Frequent: {most_frequent.name}")
            st.write(f"  Transactions: {int(most_frequent['Net Transactions']):,}")
    
    with col2:
        st.subheader("Sales Metrics")
        daily_revenue = summary['total_net_sales'] / 365
        st.write(f"• Average Transaction Value: ${avg_transaction:,.2f}")
        st.write(f"• Daily Revenue: ${daily_revenue:,.2f}")
        st.write(f"• Discount Rate: {discount_rate:.1f}%")
        loss_rate = (summary['total_loss_amount']/summary['total_net_sales']*100) if summary['total_net_sales'] > 0 else 0
        st.write(f"• Loss Rate: {loss_rate:.1f}%")

if __name__ == "__main__":
    main()
