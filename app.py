import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Hemlock Analytics", page_icon="🍸", layout="wide")

def load_data():
    try:
        df = pd.read_excel('Hemlock2023.xlsx')
        # Filter out summary rows and empty rows
        df = df[df['Order type'].isin(['Dine-in', 'Other'])]
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def create_sales_overview(df):
    # Calculate key metrics
    total_sales = df['Total sales'].sum()
    total_receipts = df['Receipts'].sum()
    avg_per_receipt = total_sales / total_receipts if total_receipts > 0 else 0

    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Sales", f"${total_sales:,.2f}")
    with col2:
        st.metric("Total Receipts", f"{total_receipts:,.0f}")
    with col3:
        st.metric("Average Per Receipt", f"${avg_per_receipt:.2f}")

    # Create sales breakdown
    st.subheader("Sales Distribution")
    
    # Bar chart
    fig = px.bar(df,
                 x='Order type',
                 y='Total sales',
                 color='Order type',
                 text=df['Total sales'].apply(lambda x: f'${x:,.0f}'),
                 title='Sales by Order Type',
                 labels={'Total sales': 'Sales ($)', 'Order type': 'Type'})
    
    fig.update_traces(textposition='outside')
    fig.update_layout(
        showlegend=False,
        xaxis_title="Order Type",
        yaxis_title="Sales ($)",
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_order_analysis(df):
    # Per-order metrics
    st.subheader("Per-Order Analysis")
    
    metrics_cols = st.columns(2)
    
    with metrics_cols[0]:
        avg_usd_cover = df['USD/cover'].mean()
        st.metric("Average USD/Cover", f"${avg_usd_cover:.2f}")
        
    with metrics_cols[1]:
        avg_usd_receipt = df['USD/receipt'].mean()
        st.metric("Average USD/Receipt", f"${avg_usd_receipt:.2f}")
    
    # Detailed metrics table
    st.subheader("Detailed Metrics by Order Type")
    
    display_df = df[['Order type', 'Total sales', 'Covers', 'Receipts', 
                     'USD/cover', 'USD/receipt', '% of Total']]
    
    formatted_df = display_df.style.format({
        'Total sales': '${:,.2f}',
        'USD/cover': '${:.2f}',
        'USD/receipt': '${:.2f}',
        '% of Total': '{:.1%}',
        'Covers': '{:,.0f}',
        'Receipts': '{:,.0f}'
    })
    
    st.dataframe(formatted_df, use_container_width=True)

def main():
    st.title("🍸 Hemlock Bar Analytics Dashboard")
    
    # Authentication
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

    df = load_data()
    
    if df is not None:
        tabs = st.tabs(["Sales Overview", "Order Analysis"])
        
        with tabs[0]:
            create_sales_overview(df)
        
        with tabs[1]:
            create_order_analysis(df)

if __name__ == "__main__":
    main()
