import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
import plotly.express as px

st.set_page_config(layout="wide", page_title="Мониторинг системы")
st.title("🖥️ Система мониторинга устройства ")

DATA_FILE = "metrics_log.csv"

refresh_options = {
    "Отключено": 0,
    "10 секунд": 10,
    "30 секунд": 30,
    "1 минута": 60,
    "5 минут": 300
}

selected_option = st.radio(
    "⏱️ Автообновление:",
    options=list(refresh_options.keys()),
    horizontal=True,
    index=1
)

refresh_interval = refresh_options[selected_option]

if st.button("🔄 Обновить данные"):
    st.rerun()

minutes = st.slider("Показать данные за последние N минут", 1, 120, 10)


def load_data():
    try:
        return pd.read_csv(DATA_FILE, parse_dates=["timestamp"])
    except FileNotFoundError:
        return pd.DataFrame()


def display_dashboard():
    data = load_data()

    if data.empty:
        st.warning("Нет доступных данных. Запусти скрипт monitoring.py.")
        return

    data["timestamp"] = pd.to_datetime(data["timestamp"])

    cutoff = datetime.now() - timedelta(minutes=minutes)
    filtered_data = data[data["timestamp"] >= cutoff]

    if filtered_data.empty:
        st.warning(f"Нет данных за последние {minutes} минут.")
        return

    filtered_data_sorted = filtered_data.sort_values('timestamp', ascending=False)

    st.subheader(f"Сырые метрики за последние {minutes} минут")

    display_data = filtered_data_sorted.copy()
    display_data['timestamp'] = display_data['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Графики")
    col1, col2 = st.columns(2)

    current_time = int(time.time() * 1000)

    with col1:
        st.plotly_chart(
            px.line(filtered_data, x="timestamp", y="cpu_percent", title="Загрузка CPU (%)"),
            use_container_width=True,
            key=f"cpu_chart_{current_time}"
        )
        st.plotly_chart(
            px.line(filtered_data, x="timestamp", y="memory_percent", title="Загрузка RAM (%)"),
            use_container_width=True,
            key=f"memory_chart_{current_time}"
        )
        st.plotly_chart(
            px.line(filtered_data, x="timestamp", y="load_avg_5min", title="Средняя нагрузка 5 мин (%)"),
            use_container_width=True,
            key=f"load1_chart_{current_time}"
        )

    with col2:
        st.plotly_chart(
            px.line(filtered_data, x="timestamp", y="disk_percent", title="Загрузка диска (%)"),
            use_container_width=True,
            key=f"disk_chart_{current_time}"
        )
        st.plotly_chart(
            px.line(filtered_data, x="timestamp", y=["net_sent", "net_recv"],
                    title="Сеть: Отправлено / Получено (байт)"),
            use_container_width=True,
            key=f"net_chart_{current_time}"
        )
        st.plotly_chart(
            px.line(filtered_data, x="timestamp", y="load_avg_15min", title="Средняя нагрузка 15 мин (%)"),
            use_container_width=True,
            key=f"load5_chart_{current_time}"
        )

    st.caption(f"Последнее обновление: {datetime.now().strftime('%H:%M:%S')}")


if refresh_interval > 0:
    dashboard_container = st.empty()

    while True:
        with dashboard_container.container():
            display_dashboard()

        time.sleep(refresh_interval)
else:
    display_dashboard()
