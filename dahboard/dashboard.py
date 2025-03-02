import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

def create_bystate_df(df):
    bystate_df = all_df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    bystate_df
    plt.figure(figsize=(10, 5))
    colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    sns.barplot(
        x="customer_count",
        y="customer_state",
        data=bystate_df.sort_values(by="customer_count", ascending=False),
        palette=colors_
    )
    plt.title("Number of Customer by States", loc="center", fontsize=15)
    plt.ylabel(None)
    plt.xlabel(None)
    plt.tick_params(axis='y', labelsize=12)
    plt.show()
    return bystate_df

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

def create_monthly_transactions_plot(all_df):
    all_df['order_purchase_timestamp'] = pd.to_datetime(all_df['order_purchase_timestamp'])

# Menambahkan kolom tambahan (tahun, bulan, hari, jam)
    all_df['year'] = all_df['order_purchase_timestamp'].dt.year
    all_df['month'] = all_df['order_purchase_timestamp'].dt.month
    all_df['day'] = all_df['order_purchase_timestamp'].dt.day
    all_df['hour'] = all_df['order_purchase_timestamp'].dt.hour
    all_df['weekday'] = all_df['order_purchase_timestamp'].dt.weekday
# Melihat distribusi transaksi per bulan
    monthly_transactions = all_df.groupby('month').size()
    monthly_transactions.plot(kind='bar', title='Distribusi Transaksi per Bulan')
    return monthly_transactions

def create_payment_distribution_plot(all_df):
    # Menghitung distribusi pembayaran berdasarkan tipe pembayaran dan bulan
    payment_distribution = all_df.groupby(['payment_type', 'month']).size().unstack()

    # Membuat plot
    fig, ax = plt.subplots(figsize=(10, 6))
    payment_distribution.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        title='Metode Pembayaran per Bulan'
    )
    ax.set_ylabel('Jumlah Transaksi')
    ax.set_xlabel('Tipe Pembayaran')
    ax.legend(title='Bulan', loc='upper right')
    st.pyplot(fig)

    return payment_distribution

def create_heatmap_plot(all_df):
    heatmap_data = all_df.groupby(['weekday', 'hour']).size().unstack()

    # Plotting heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(heatmap_data, cmap='YlGnBu', linewidths=0.5, annot=True, fmt="g", ax=ax)
    ax.set_title('Pola Transaksi Harian', fontsize=16)
    ax.set_xlabel('Jam', fontsize=12)
    ax.set_ylabel('Hari', fontsize=12)
    plt.tight_layout()

    st.pyplot(fig)
    return heatmap_data

# Fungsi untuk membuat plot pembayaran per jam
def create_hourly_payment_plot(all_df):
    hourly_payment = all_df.groupby(['hour', 'payment_type']).size().unstack(fill_value=0)

    # Membuat plot menggunakan Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6))
    hourly_payment.plot(kind='bar', stacked=True, ax=ax)

    ax.set_title('Metode Pembayaran per Jam', fontsize=16)
    ax.set_xlabel('Jam', fontsize=12)
    ax.set_ylabel('Jumlah Transaksi', fontsize=12)
    ax.legend(title='Metode Pembayaran', fontsize=10)

    # Tampilkan plot di Streamlit
    st.pyplot(fig)

    # Return data untuk referensi atau kebutuhan tambahan
    return hourly_payment

def create_rfm_df(all_df):
    all_df['customer_id'] = pd.factorize(all_df['customer_id'])[0]

    # Lanjutkan proses grupby seperti biasa
    rfm_df = all_df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",  # mengambil tanggal order terakhir
        "order_id": "nunique",  # menghitung jumlah order
        "payment_value": "sum"  # menghitung jumlah revenue yang dihasilkan
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
all_df.head()

all_df.info()

# Tentukan kolom yang tidak digunakan
kolom_tidak_digunakan = ['customer_unique_id', 'order_approved_at', 'order_status', 'payment_sequential', 'payment_installments', 'shipping_limit_date',
                         'product_name_lenght', 'product_description_lenght','product_height_cm', 'product_width_cm', 'product_length_cm', 'product_photos_qty',
                         'freight_value', 'order_delivered_carrier_date', 'order_estimated_delivery_date', 'order_item_id', 'price','product_weight_g',
                         'seller_state']
all_df = all_df.drop(columns=kolom_tidak_digunakan) # Pass the list of columns to the 'columns' parameter of the drop method

print("\nDataFrame setelah menghapus kolom yang tidak digunakan:")
print(all_df.head()) # Print the head to verify the changes

# melihat daftar kolom setelah dilakukan penghapusan kolom irrelevant
all_df.info()

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) &
                (all_df["order_purchase_timestamp"] <= str(end_date))]

bystate_df = create_bystate_df(main_df)
monthly_orders_df = create_monthly_orders_plot(main_df)
monthly_transactions = create_monthly_transactions_plot(main_df)
payment_distribution = create_payment_distribution_plot(main_df)
heatmap_data = create_heatmap_plot(main_df)
hourly_payment = create_hourly_payment_plot(main_df)
rfm_df = create_rfm_df(main_df)

st.header('Dashboard Data Penjualan E-Commerce')

"""### **Plot Monthly Orders**"""

st.subheader('Monthly Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "BRL", locale='es_CO')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_orders_df["order_purchase_timestamp"],
    monthly_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

"""### **Plot Customer Demographics**"""

st.subheader('Customer Demographics')

fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9"] + ["#D3D3D3"] * (len(bystate_df["customer_state"].unique()) - 1)
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    palette=colors,
    ax=ax,
    hue=None
)
ax.set_title("Number of Customer by States", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

"""### Plot **Payment Type Distribution**"""

def main():
    st.subheader("Distribusi Metode Pembayaran per Bulan")

    # Dummy DataFrame
    data = {
        'payment_type': ['Credit Card', 'Debit Card', 'Boleto', 'Voucher', 'Credit Card', 'Debit Card', 'Boleto', 'Voucher'] * 2,
        'month': ['January', 'January', 'January','January','February', 'February', 'February', 'February'] * 2,
        'transaction_id': range(1, 17)
    }
    all_df = pd.DataFrame(data)

    st.subheader("Data Transaksi")
    st.dataframe(all_df)

    st.subheader("Distribusi Metode Pembayaran")
    payment_distribution = create_payment_distribution_plot(all_df)

    st.subheader("Tabel Distribusi")
    st.dataframe(payment_distribution)

if __name__ == '__main__':
    main()

"""### **Plot Pola Transaksi Harian**"""

st.subheader("Visualisasi Pola Transaksi Harian")
st.write("Aplikasi ini menampilkan heatmap pola transaksi berdasarkan hari dan jam.")

# Simulasi data (ganti dengan dataframe sebenarnya)
data = {
    "weekday": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"] * 24,
    "hour": list(range(24)) * 7  # Create a list of hours for each day
}
all_df = pd.DataFrame(data)

# Pastikan dataframe memiliki kolom 'weekday' dan 'hour'
if 'weekday' in all_df.columns and 'hour' in all_df.columns:
    st.subheader("Heatmap Pola Transaksi Harian")
    heatmap_data = create_heatmap_plot(all_df)

    # Display raw data preview
    st.subheader("Data Ringkasan Heatmap")
    st.write(heatmap_data)
else:
    st.error("Dataframe harus memiliki kolom 'weekday' dan 'hour'.")

"""### **Plot Payment Type per Hour**"""

st.subheader("Analisis Metode Pembayaran per Jam")

# Jika dataframe sudah ada
st.write("Data berhasil dimuat. Berikut adalah preview:")
st.dataframe(main_df.head())  # Menampilkan preview data (gunakan dataframe yang sudah ada)

# Menjalankan fungsi untuk membuat plot
st.subheader("Visualisasi Metode Pembayaran per Jam")
hourly_payment = create_hourly_payment_plot(main_df)

# Menampilkan tabel hasil grup
st.subheader("Tabel Metode Pembayaran per Jam")
st.dataframe(hourly_payment)

st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO')
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
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
