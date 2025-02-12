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
    """Load and process data with improved categorization"""
    try:
        df = pd.read_excel('Pine.xlsx', sheet_name='2023 Product Breakdown')
        
        # Calculate net metrics for each product
        df['Net Amount'] = df['Transaction Amount'].fillna(0) - df['Loss Amount'].fillna(0) - df['Returned Amount'].fillna(0)
        df['Net Quantity'] = df['Transaction Quantity'].fillna(0) - df['Loss Quantity'].fillna(0) - df['Returned Quantity'].fillna(0)
        df['Net Transactions'] = df['Transaction Count'].fillna(0) - df['Loss Transaction Count'].fillna(0) - df['Returned Transaction Count'].fillna(0)
        
        # Get main categories
        categories = df[df['SKU'].isna()].index
        
        # Process products with categories
        products_by_category = {}
        for i in range(len(categories)-1):
            category_products = df.iloc[categories[i]+1:categories[i+1]]
            products_by_category[df.iloc[categories[i]].name] = category_products
        
        # Calculate summary metrics
        summary = {
            'total_net_sales': df['Net Amount'].sum(),
            'total_net_quantity': df['Net Quantity'].sum(),
            'total_net_transactions': df['Net Transactions'].sum(),
            'total_discounted_amount': abs(df['Discounted Amount'].fillna(0).sum()),
            'total_loss_amount': abs(df['Loss Amount'].fillna(0).sum())
        }
        
        return df, products_by_category, summary
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None, None

def create_bar_chart(df, title, metric='Net Amount', show_category=False):
    """Create an improved bar chart with proper labeling"""
    data = df.copy()
    if show_category:
        data['Category'] = data.index.map(lambda x: 'Food' if 'FOOD' in str(x).upper() 
                                        else 'Drinks' if any(s in str(x).upper() for s in ['COCKTAIL', 'SPIRIT', 'WINE', 'BEER']) 
                                        else 'Other')
    
    fig = go.Figure()
    
    if show_category:
        for category in data['Category'].unique():
            cat_data = data[data['Category'] == category]
            fig.add_trace(go.Bar(
                x=cat_data.index,
                y=cat_data[metric],
                name=category
            ))
    else:
        fig.add_trace(go.Bar(
            x=data.index,
            y=data[metric],
            text=data[metric].apply(lambda x: f'${x:,.2f}' if 'Amount' in metric else f'{x:,.0f}'),
            textposition='auto',
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Product",
        yaxis_title="Revenue ($)" if 'Amount' in metric else "Quantity",
        height=400,
        xaxis_tickangle=-45,
        margin=dict(t=50, l=50, r=20, b=100),
        showlegend=show_category
    )
    return fig

def main():
    st.title("🍸 Pris Bar Analytics Dashboard")
    
    df, products_by_category, summary = load_and_process_data()
    if df is None or products_by_category is None:
        return

    # Category Analysis
    st.header("Revenue by Category")
    category_totals = {}
    for category, products in products_by_category.items():
        if not category.startswith('Grand'):  # Exclude grand totals
            category_totals[category] = products['Net Amount'].sum()
    
    category_df = pd.DataFrame.from_dict(category_totals, orient='index', columns=['Net Amount'])
    category_df = category_df.sort_values('Net Amount', ascending=False)
    
    fig_categories = create_bar_chart(category_df, "Revenue by Category")
    st.plotly_chart(fig_categories, use_container_width=True)

    # Top Products
    st.header("Top Products")
    col1, col2 = st.columns(2)
    
    # Get products only (rows with SKUs)
    products_df = df[df['SKU'].notna() & (df['Net Amount'] > 0)].copy()
    
    with col1:
        top_revenue = products_df.nlargest(10, 'Net Amount')
        fig_revenue = create_bar_chart(top_revenue, "Top 10 Products by Revenue")
        st.plotly_chart(fig_revenue, use_container_width=True)
    
    with col2:
        top_quantity = products_df.nlargest(10, 'Net Quantity')
        fig_quantity = create_bar_chart(top_quantity, "Top 10 Products by Quantity", 'Net Quantity')
        st.plotly_chart(fig_quantity, use_container_width=True)

    # Detailed Analysis
    st.header("Category Details")
    
    # Create tabs for each major category
    tabs = st.tabs([cat for cat in products_by_category.keys() if not cat.startswith('Grand')])
    
    for tab, (category, products) in zip(tabs, products_by_category.items()):
        if not category.startswith('Grand'):
            with tab:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Top Products")
                    top_products = products[products['Net Amount'] > 0].nlargest(5, 'Net Amount')
                    for _, product in top_products.iterrows():
                        st.write(f"• {product.name}")
                        st.write(f"  Revenue: ${product['Net Amount']:,.2f}")
                        st.write(f"  Quantity: {int(product['Net Quantity']):,}")
                
                with col2:
                    st.subheader("Category Metrics")
                    total_revenue = products['Net Amount'].sum()
                    total_quantity = products['Net Quantity'].sum()
                    discount_rate = abs(products['Discounted Amount'].sum() / total_revenue * 100)
                    
                    st.write(f"• Total Revenue: ${total_revenue:,.2f}")
                    st.write(f"• Total Quantity: {int(total_quantity):,}")
                    st.write(f"• Discount Rate: {discount_rate:.1f}%")
                    st.write(f"• Average Price: ${total_revenue/total_quantity:.2f}")

if __name__ == "__main__":
    main()
