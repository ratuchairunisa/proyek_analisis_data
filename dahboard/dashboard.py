import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import altair as alt
from babel.numbers import format_currency

sns.set(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe

def create_monthly_orders_plot(all_df):
    monthly_orders_df = all_df.resample(rule='M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    }).reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)

    plt.figure(figsize=(10, 5))
    plt.plot(monthly_orders_df["order_purchase_timestamp"], monthly_orders_df["order_count"], marker='o', linewidth=2, color="#72BCD4")
    plt.title("Number of Orders per Month (2018)", loc="center", fontsize=20)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.show()
    return monthly_orders_df

def create_rfm_df(all_df):
    all_df['customer_id'] = pd.factorize(all_df['customer_id'])[0]

    # Lanjutkan proses grupby seperti biasa
    rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",  
        "order_id": "nunique",  
        "payment_value": "sum" 
    })

    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # Menghitung recency
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = all_df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)

    # Menghapus kolom max_order_timestamp
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    rfm_df.head()
    return rfm_df

all_df = pd.read_csv("dahboard/all_data.csv.gz")

# Tentukan kolom yang tidak digunakan
kolom_tidak_digunakan = ['customer_unique_id', 'order_approved_at', 'order_status', 'payment_sequential', 'payment_installments', 'shipping_limit_date',
                         'product_name_lenght', 'product_description_lenght','product_height_cm', 'product_width_cm', 'product_length_cm', 'product_photos_qty',
                         'freight_value', 'order_delivered_carrier_date', 'order_estimated_delivery_date', 'order_item_id', 'price','product_weight_g',
                         'seller_state']
all_df = all_df.drop(columns=kolom_tidak_digunakan) 


datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo 
    st.title("**Welcome to Ratu Chairunisa's Dashboard** :bar_chart:")
    st.image("logo public e commerce.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                (all_df["order_purchase_timestamp"] <= str(end_date))]

monthly_orders_df = create_monthly_orders_plot(main_df)
rfm_df = create_rfm_df(main_df)

# pesanan bulanan
st.header('Dashboard Data Penjualan E-Commerce :rose:')
st.subheader('Pesanan Bulanan')

# Date selection
min_date = monthly_orders_df["order_purchase_timestamp"].min().date()
max_date = monthly_orders_df["order_purchase_timestamp"].max().date()
selected_date = st.date_input("Pilih Tanggal", min_value=min_date, max_value=max_date, value=min_date)

# Filter data
filtered_df = monthly_orders_df[monthly_orders_df["order_purchase_timestamp"].dt.date <= selected_date]

# Metrics
total_orders = filtered_df.order_count.sum()
total_revenue = format_currency(filtered_df.revenue.sum(), "IDR", locale='id_ID')

col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders, delta=0.5)

with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "BRL", locale='pt_BR')
    st.metric("Total Revenue", value=total_revenue, delta=0.5)

st.line_chart(monthly_orders_df.set_index("order_purchase_timestamp"))

st.markdown('''Dari line chart di atas menunjukkan fluktuasi pada jumlah pesanan dimana terjadi kenaikan pesanan 
yang tinggi pada bulan Desember 2017 dan terjadi penurunan pesanan drastis pada bulan Oktober 2018''')

# Distribusi Pembayaran Setiap Bulan
st.subheader("Distribusi Metode Pembayaran per Bulan")

all_df['month'] = all_df['order_purchase_timestamp'].dt.month
all_df['hour'] = all_df['order_purchase_timestamp'].dt.hour
all_df['payment_type'] = all_df['payment_type'].str.replace("_", " ").str.title()


st.bar_chart(all_df, x="month", y="payment_value", color="payment_type", horizontal=True)

st.markdown('''Bar chart di atas diketahui bahwa transaksi paling banyak dilakukan pada bulan 5 dan transaksi paling sedikit dilakukan pada
bulan 9''')

# Melihat Metode Pembayaran per Jam
st.subheader("Tren Perubahan Volume Transaksi Sepanjang Hari")
payment_chart = alt.Chart(all_df).mark_bar(opacity=0.7).encode(
    x=alt.X("hour:O", title="Jam (00:00 - 23:59)"),
    y=alt.Y("payment_value:Q", title="Jumlah Transaksi"),
    color="payment_type:N",
    tooltip=["hour", "payment_type", "payment_value"]
).properties(
    width=700, height=400
)
st.altair_chart(payment_chart, use_container_width=True)

st.markdown('''Pada hstacked bar chart di atas, pola transaksi harian paling banyak dilakukan 
pada jam 14.00-15.00 dengan metode pembayaran menggunakan credit card''')

# Menampilkan Produk Paling Banyak di Beli
st.subheader("Top 5 Kategori Produk Paling Banyak Terjual Berdasarkan Score Review")
st.write(all_df.groupby(by=['product_category_name', 'review_score']).agg({
    "order_id": "nunique",
    "payment_value": "sum"
}).sort_values(by="payment_value", ascending=False). head(5))

st.markdown('''Dari tabel di atas diketahui bahwa kategori produk yang paling laris adalah beleza_saude (health beauty) dengan review score 5 
dan memberikan nilai pembayaran (payment_value) terbesar''')


# RFM analisis
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "BRL", locale='pt_BR')
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.markdown('''
- Pada bar chart :blue-background[Recency] menunjukkan rata-rata jumlah hari sejak terakhir kali customer melakukan transaksi yaitu sekitar 241 hari yang lalu
- Pada bar chart :blue-background[Frequency] menunjukkan jumlah total transaksi yang dilakukan oleh customer. pada chart tersebut diketahui bahwa sejumlah customer rata-rata melakukan transaksi pemesanan sebanyak satu kali
- Pada bar chart :blue-background[Monetary] menunjukkan total pembayaran yang dilakukan customer. pada chart tersebut menunjukkan ada 1455 customer yang mengeluarkan uang hingga 110.000 BRL
''')

