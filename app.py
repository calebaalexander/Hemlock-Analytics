import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="Hemlock Analytics", page_icon="🍸", layout="wide")

def clean_numeric(value):
    """Clean numeric values from currency and formatting"""
    if isinstance(value, str):
        return pd.to_numeric(value.replace('$', '').replace(',', ''), errors='coerce')
    return value

def load_data():
    try:
        df = pd.read_excel('Hemlock2023.xlsx')
        
        # Clean numeric columns
        numeric_columns = ['Total sales', 'USD/cover', 'USD/receipt']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_numeric)
        
        # Convert percentage columns
        pct_columns = ['% of Total', '% of Total.1', '% of Total.2']
        for col in pct_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: float(str(x).rstrip('%')) / 100 if pd.notnull(x) else x)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def format_currency(value):
    """Format number as currency"""
    return f"${value:,.2f}"

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
        tabs = st.tabs(["Sales Overview", "Detailed Analysis"])
        
        with tabs[0]:
            st.header("Sales Overview")
            
            # Top-level metrics
            metrics_cols = st.columns(3)
            with metrics_cols[0]:
                total_sales = df['Total sales'].sum()
                st.metric("Total Sales", format_currency(total_sales))
            
            with metrics_cols[1]:
                total_receipts = df['Receipts'].sum()
                st.metric("Total Receipts", f"{total_receipts:,.0f}")
            
            with metrics_cols[2]:
                avg_per_receipt = total_sales / total_receipts if total_receipts > 0 else 0
                st.metric("Average Per Receipt", format_currency(avg_per_receipt))
            
            # Daily average metrics
            st.subheader("Performance Metrics")
            daily_cols = st.columns(2)
            with daily_cols[0]:
                avg_cover = df['USD/cover'].mean()
                st.metric("Average USD/Cover", format_currency(avg_cover))
            
            with daily_cols[1]:
                avg_receipt = df['USD/receipt'].mean()
                st.metric("Average USD/Receipt", format_currency(avg_receipt))
            
            # Sales visualization
            st.subheader("Sales Distribution")
            fig = px.bar(df,
                        x='Order type',
                        y='Total sales',
                        title='Sales by Order Type',
                        color='Order type',
                        labels={'Total sales': 'Sales ($)', 'Order type': 'Type'})
            
            fig.update_layout(showlegend=False,
                            xaxis_title="Order Type",
                            yaxis_title="Sales ($)")
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed metrics table
            st.subheader("Detailed Metrics")
            formatted_df = df.copy()
            formatted_df['Total sales'] = formatted_df['Total sales'].apply(format_currency)
            formatted_df['USD/cover'] = formatted_df['USD/cover'].apply(format_currency)
            formatted_df['USD/receipt'] = formatted_df['USD/receipt'].apply(format_currency)
            st.dataframe(formatted_df.style.format({
                '% of Total': '{:.1%}',
                '% of Total.1': '{:.1%}',
                '% of Total.2': '{:.1%}'
            }))
        
        with tabs[1]:
            st.header("Detailed Analysis")
            
            # Order type analysis
            selected_type = st.selectbox("Select Order Type", df['Order type'].unique())
            type_data = df[df['Order type'] == selected_type]
            
            if not type_data.empty:
                st.subheader(f"Metrics for {selected_type}")
                type_cols = st.columns(3)
                with type_cols[0]:
                    st.metric("Sales", format_currency(type_data['Total sales'].iloc[0]))
                with type_cols[1]:
                    st.metric("% of Total Sales", f"{type_data['% of Total'].iloc[0]:.1%}")
                with type_cols[2]:
                    st.metric("Average Ticket", format_currency(type_data['USD/receipt'].iloc[0]))

if __name__ == "__main__":
    main()
