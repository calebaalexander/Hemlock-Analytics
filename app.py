import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Hemlock Bar Analytics",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }
    .big-number {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .small-number {
        font-size: 1rem;
        color: #666;
    }
    .metric-title {
        font-size: 0.875rem;
        color: #666;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

def load_sales_data():
    try:
        df = pd.read_excel('Hemlock2023.xlsx')
        # Filter out summary and empty rows
        df = df[df['Order type'].isin(['Dine-in', 'Other'])]
        return df
    except Exception as e:
        st.error(f"Error loading sales data: {str(e)}")
        return None

def create_metric_card(title, value, comparison=None, delta=None):
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="big-number">{value}</div>
            {f'<div class="small-number">{comparison}</div>' if comparison else ''}
            {f'<div class="small-number {delta}">{delta}</div>' if delta else ''}
        </div>
    """, unsafe_allow_html=True)

def main():
    st.title("🍸 Hemlock Bar Performance Dashboard")

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

    df = load_sales_data()
    if df is not None:
        # Top-level metrics
        st.subheader("Key Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_revenue = df['Total sales'].sum()
            avg_revenue_per_day = total_revenue / 30  # Assuming monthly data
            st.metric(
                "Total Revenue",
                f"${total_revenue:,.0f}",
                f"${avg_revenue_per_day:,.0f}/day avg"
            )
        
        with col2:
            total_orders = df['Receipts'].sum()
            avg_orders_per_day = total_orders / 30
            st.metric(
                "Total Orders",
                f"{total_orders:,.0f}",
                f"{avg_orders_per_day:.0f}/day avg"
            )
        
        with col3:
            avg_ticket = total_revenue / total_orders
            st.metric(
                "Average Check",
                f"${avg_ticket:.2f}",
                help="Average spend per order"
            )
        
        with col4:
            total_covers = df['Covers'].sum()
            revenue_per_cover = total_revenue / total_covers
            st.metric(
                "Revenue per Cover",
                f"${revenue_per_cover:.2f}",
                f"{total_covers:,} total covers"
            )

        # Service Type Analysis
        st.subheader("Service Type Analysis")
        cols = st.columns([2, 1])
        
        with cols[0]:
            # Create comparison table
            comparison_data = []
            for service_type in df['Order type'].unique():
                service_df = df[df['Order type'] == service_type]
                comparison_data.append({
                    'Service Type': service_type,
                    'Revenue': service_df['Total sales'].iloc[0],
                    'Orders': service_df['Receipts'].iloc[0],
                    'Covers': service_df['Covers'].iloc[0],
                    'Avg Check': service_df['Total sales'].iloc[0] / service_df['Receipts'].iloc[0],
                    'Revenue/Cover': service_df['Total sales'].iloc[0] / service_df['Covers'].iloc[0],
                    '% of Revenue': service_df['Total sales'].iloc[0] / total_revenue * 100
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(
                comparison_df.style.format({
                    'Revenue': '${:,.0f}',
                    'Orders': '{:,.0f}',
                    'Covers': '{:,.0f}',
                    'Avg Check': '${:.2f}',
                    'Revenue/Cover': '${:.2f}',
                    '% of Revenue': '{:.1f}%'
                }),
                use_container_width=True
            )
        
        with cols[1]:
            # Revenue Distribution
            fig = go.Figure(data=[go.Pie(
                labels=df['Order type'],
                values=df['Total sales'],
                textinfo='label+percent',
                textposition='inside',
                hole=.4
            )])
            
            fig.update_layout(
                title="Revenue Distribution",
                showlegend=False,
                annotations=[dict(text='Revenue', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)

        # Performance Insights
        st.subheader("Performance Insights")
        insight_cols = st.columns(2)
        
        with insight_cols[0]:
            st.markdown("##### Revenue Metrics")
            st.markdown(f"""
                - Highest revenue service type: **{comparison_df.iloc[comparison_df['Revenue'].argmax()]['Service Type']}** 
                  (${comparison_df['Revenue'].max():,.0f})
                - Average order value: **${avg_ticket:.2f}**
                - Revenue per cover: **${revenue_per_cover:.2f}**
            """)
        
        with insight_cols[1]:
            st.markdown("##### Operational Metrics")
            st.markdown(f"""
                - Total covers served: **{total_covers:,}**
                - Average orders per day: **{avg_orders_per_day:.0f}**
                - Revenue per day: **${avg_revenue_per_day:,.0f}**
            """)

if __name__ == "__main__":
    main()
