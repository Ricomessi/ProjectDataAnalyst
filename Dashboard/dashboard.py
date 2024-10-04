import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

st.title("Dashboard Analisis Kualitas Udara")
st.write("Dashboard ini memberikan wawasan mengenai data kualitas udara dari berbagai stasiun selama beberapa waktu.")

@st.cache_data
def load_data():
    data_path = 'Dashboard/PRSA_Data_20130301-20170228'
    dataset_list = os.listdir(data_path)
    dataframes = []
    
    for filename in dataset_list:
        if filename.endswith('.csv'):
            file_path = os.path.join(data_path, filename)
            df = pd.read_csv(file_path)
            df.interpolate(method='linear', inplace=True)
            dataframes.append(df)
    
    all_data = pd.concat(dataframes, ignore_index=True)
    return all_data

all_data = load_data()

st.sidebar.title("Pilihan Pengguna")

pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
selected_pollutants = st.sidebar.multiselect('Pilih Polutan', pollutants, default=pollutants)

st.sidebar.subheader("Pilih Rentang Waktu")
hour_range = st.sidebar.slider('Jam', 0, 23, (0, 23))

filtered_data = all_data[(all_data['hour'] >= hour_range[0]) & (all_data['hour'] <= hour_range[1])]

st.subheader("Statistik Deskriptif")
stats = filtered_data[selected_pollutants].describe()
st.write(stats)

hourly_avg = filtered_data.groupby('hour')[selected_pollutants].mean()

st.subheader("Rata-rata Konsentrasi Polutan per Jam")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for i, pollutant in enumerate(selected_pollutants):
    axes[i].plot(hourly_avg.index, hourly_avg[pollutant], label=pollutant)
    axes[i].set_title(f'Rata-rata {pollutant} per Jam')
    axes[i].set_xlabel('Jam')
    axes[i].set_ylabel('Konsentrasi')

for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
st.pyplot(fig)

st.subheader("Stasiun dengan Konsentrasi NO2 Tertinggi")

station_avg_no2 = all_data.groupby('station')['NO2'].mean()
highest_avg_no2_station = station_avg_no2.idxmax()
highest_avg_no2_value = station_avg_no2.max()

st.write(f"Stasiun dengan rata-rata konsentrasi NO2 tertinggi adalah **{highest_avg_no2_station}** dengan nilai **{highest_avg_no2_value:.2f}**.")

st.subheader("Konsentrasi NO2 per Stasiun")
plt.figure(figsize=(10, 6))
sns.barplot(x=station_avg_no2.index, y=station_avg_no2.values)
plt.title('Rata-rata Konsentrasi NO2 per Stasiun')
plt.xlabel('Stasiun')
plt.ylabel('Rata-rata Konsentrasi NO2')
plt.xticks(rotation=45)
st.pyplot(plt)

st.sidebar.subheader("Pilih Stasiun")
stations = all_data['station'].unique()
selected_station = st.sidebar.selectbox("Pilih Stasiun", stations)

station_data = all_data[all_data['station'] == selected_station]

st.subheader(f"Konsentrasi Polutan di Stasiun {selected_station}")
for pollutant in selected_pollutants:
    plt.figure(figsize=(12, 6))
    plt.plot(station_data.index, station_data[pollutant], label=pollutant)
    plt.title(f'Konsentrasi {pollutant} di Stasiun {selected_station}')
    plt.xlabel('Waktu')
    plt.ylabel('Konsentrasi')
    plt.legend()
    st.pyplot(plt)
