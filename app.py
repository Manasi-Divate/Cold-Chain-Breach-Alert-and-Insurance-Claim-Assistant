import streamlit as st
import pandas as pd

from utils.data_loader import load_data, validate_columns, prepare_timestamp
from utils.data_cleaner import clean_data, create_features, get_summary
from utils.breach_detector import detect_excursions, get_excursion_statistics
from utils.visualizer import (
    temperature_graph,
    humidity_graph,
    health_index_graph,
    temperature_distribution,
    route_analysis,
    product_analysis,
)

st.set_page_config(
    page_title='Cold Chain Breach Alert & Insurance Claim Assistant',
    layout='wide',
)

st.markdown("""
# ❄️ Cold Chain Breach Alert & Insurance Claim Assistant

Upload an IoT healthcare shipment dataset and analyze:
- Temperature Breaches
- Excursion Severity
- Shipment Health
- Insurance Claim Recommendation
""")

uploaded_file = st.file_uploader(
    'Upload CSV Dataset',
    type=['csv'],
)

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        missing_columns = validate_columns(df)

        if missing_columns:
            st.error(
                f'Missing required dataset columns: {", ".join(missing_columns)}'
            )
        else:
            df = prepare_timestamp(df)
            df = clean_data(df)
            df = create_features(df)

            summary = get_summary(df)
            excursions = detect_excursions(df)
            stats = get_excursion_statistics(excursions)
            excursion_df = pd.DataFrame(excursions)

            st.header('📊 Dataset Summary')
            c1, c2, c3, c4 = st.columns(4)
            c1.metric('Records', summary['records'])
            c2.metric('Average Temp', f"{summary['avg_temp']} °C")
            c3.metric('Average Humidity', f"{summary['avg_humidity']} %")
            c4.metric('Average Health Index', summary['avg_health'])

            st.header('🚨 Breach Dashboard')
            c1, c2, c3, c4 = st.columns(4)
            c1.metric('Total Excursions', stats['total_excursions'])
            c2.metric('Average Duration', f"{stats['avg_duration']} min")
            c3.metric('Longest Duration', f"{stats['longest_duration']} min")
            c4.metric('Maximum Temperature', f"{stats['max_temperature']} °C")

            st.header('📝 Insurance Claim Recommendation')
            if stats['max_temperature'] > 10:
                st.error(
                    'Claim Recommended: Temperature exceeded critical cold-chain limits.'
                )
            elif stats['max_temperature'] > 8:
                st.warning(
                    'Moderate Risk Detected: Manual inspection recommended before claim decision.'
                )
            else:
                st.success('Low Risk Shipment: No insurance claim required.')

            st.header('📋 Excursion Details')
            if not excursion_df.empty:
                st.dataframe(excursion_df, use_container_width=True)
            else:
                st.success('No temperature excursions detected.')

            st.header('📈 Visual Analytics')
            st.plotly_chart(temperature_graph(df), use_container_width=True)
            st.plotly_chart(humidity_graph(df), use_container_width=True)
            st.plotly_chart(health_index_graph(df), use_container_width=True)
            st.plotly_chart(temperature_distribution(df), use_container_width=True)
            st.plotly_chart(route_analysis(df), use_container_width=True)
            st.plotly_chart(product_analysis(df), use_container_width=True)

    except Exception as e:
        st.error(f'Application Error: {e}')
