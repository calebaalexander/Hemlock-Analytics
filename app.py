import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Hemlock Analytics", page_icon="🍸", layout="wide", initial_sidebar_state="collapsed")

def load_data():
    try:
        df = pd.read_excel('Hemlock2023.xlsx')
        # Remove summary and empty rows
        df = df[df['Order type'].isin(['Dine-in', 'Other'])]
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def main():
    st.title("🍸 Hemlock Bar Analytics")
    
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
        # Main metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue", f"${df['Total sales'].sum():,.2f}")
        with col2:
            st.metric("Total Orders", f"{df['Receipts'].sum():,.0f}")
        with col3:
            avg_ticket = df['Total sales'].sum() / df['Receipts'].sum()
            st.metric("Average Ticket", f"${avg_ticket:.2f}")
        with col4:
            total_covers = df['Covers'].sum()
            st.metric("Total Covers", f"{total_covers:,.0f}")

        # Create two columns for the dashboard
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.subheader("Revenue Analysis")
            
            # Revenue by service type
            fig = px.pie(df, 
                        values='Total sales',
                        names='Order type',
                        title='Revenue Distribution by Service Type',
                        color_discrete_sequence=['#2E86C1', '#28B463'])
            fig.update_traces(textinfo='percent+value',
                            texttemplate='%{percent:.1%}<br>$%{value:,.0f}')
            st.plotly_chart(fig, use_container_width=True)

            # Show key performance metrics table
            st.subheader("Service Type Performance")
            metrics_df = df.copy()
            metrics_df['Revenue Per Cover'] = metrics_df['Total sales'] / metrics_df['Covers']
            metrics_df['Revenue Per Order'] = metrics_df['Total sales'] / metrics_df['Receipts']
            
            display_df = metrics_df[[
                'Order type', 'Total sales', 'Covers', 'Receipts',
                'Revenue Per Cover', 'Revenue Per Order'
            ]].reset_index(drop=True)
            
            st.dataframe(
                display_df.style.format({
                    'Total sales': '${:,.2f}',
                    'Revenue Per Cover': '${:,.2f}',
                    'Revenue Per Order': '${:,.2f}',
                    'Covers': '{:,.0f}',
                    'Receipts': '{:,.0f}'
                }),
                use_container_width=True
            )

        with right_col:
            st.subheader("Key Metrics")
            
            # Service type comparison
            for service_type in df['Order type'].unique():
                service_data = df[df['Order type'] == service_type]
                st.markdown(f"#### {service_type}")
                
                metrics_cols = st.columns(2)
                with metrics_cols[0]:
                    st.metric("Avg Check",
                             f"${service_data['USD/receipt'].iloc[0]:.2f}")
                with metrics_cols[1]:
                    st.metric("Cover Count",
                             f"{service_data['Covers'].iloc[0]:,.0f}")
                
                # Add percentage of total sales
                pct_sales = service_data['Total sales'].iloc[0] / df['Total sales'].sum()
                st.markdown(f"**% of Sales:** {pct_sales:.1%}")
                st.markdown(f"**Revenue:** ${service_data['Total sales'].iloc[0]:,.2f}")
                st.markdown("---")

if __name__ == "__main__":
    main()
