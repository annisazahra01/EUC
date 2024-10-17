import numpy as np
import pandas as pd
from collections import Counter
from datetime import datetime
from copy import copy
from IPython.display import display, HTML
import streamlit as st # type: ignore
from streamlit_echarts import st_echarts # type: ignore
import json
import requests
from datetime import datetime
import calendar
import re

divider_style = """
    <hr style="border: none; 
    height: 5px; 
    background-color: black; 
    border-radius: 10px; 
    margin: 20px 0;
    opacity: 0.8">
"""

# Set Streamlit to use the wider layout mode
st.set_page_config(layout="wide", page_title="EUC QA")


def create_pie_chart(miss_data, corr_data, a, b):
    options = {
        "tooltip": {"trigger": "item"},
        "legend": {
            "top": "5%",
            "left": "center",
            "textStyle": {"color": "#000"}  # Legend text color to white
        },
        "series": [
            {
                "name": "Rasio Konsistensi",
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 0,
                    "borderColor": "#000",
                    "borderWidth": 0,
                },
                "label": {
                    "show": False,
                    "position": "center",
                    "color": "#000",  # Text color white
                    "fontSize": 16,
                    "fontWeight": "bold"
                },
                "labelLine": {"show": False},
                "data": [
                    {"value": miss_data, "name": b, "itemStyle": {"color": "#ff6961"}},  # Soft red for mismatch
                    {"value": corr_data, "name": a, "itemStyle": {"color": "#90ee90"}},  # Soft green for correct
                ],
            }
        ],
    }

    st_echarts(
        options=options, height="300px",
    )


def main():

    # Custom CSS to center the title
    st.markdown("""
        <style>
        .centered-title {
            text-align: center;
            text-decoration: underline;
        }
        </style>
        """, unsafe_allow_html=True)

    # Centered title using custom class
    st.markdown("<h1 class='centered-title'>LAPORAN SEKDA QUALITY ASSURANCE</h1>", unsafe_allow_html=True)
    st.markdown(divider_style, unsafe_allow_html=True)

    # Centralized styling for the DataFrames
    dataframe_style = {
        'text-align': 'center',
        'background-color': '#E8F6F3'
    }

    def highlight_rows(row):
        # Index will be used to check the first and last rows
        if pd.notna(row['Komponen']) and row['Komponen'].strip() != '':
            return ['background-color: #A9DFBF; color: black'] * len(row)  # Green background
        # Check if 'Keterangan' is exactly 'Selisih'
        elif row['Keterangan'] == 'Selisih':
            return ['background-color: #F1948A; color: black'] * len(row)  # Red background
        else:
            return ['background-color: #F9E79F; color: black'] * len(row)  # Yellow background for other rows

    # Function to display the DataFrame
    def display_dataframe(input_df):
        st.dataframe(input_df.style.set_properties(**{'text-align': 'center'}).set_table_styles(
            [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
        ).format(precision=2))

    file_path = "https://raw.githubusercontent.com/annisazahra01/EUC/0a41a0356c77d2b15d9507584531e55ab350b350/data_verhor3.json"

    # Load the JSON file
    response = requests.get(file_path)
    data = response.json()

    #file_path = "C:\\Users\\annis\\Downloads\\Ferro\\data_verhor3.json"

    # Load the JSON file
    #with open(file_path, 'r') as f:
    #    data = json.load(f)

    raw_data = data['vertikal_data_raw']
    raw_keys_list = list(raw_data.keys())

    clean_data = data['vertikal_data_clean']
    clean_keys_list = list(clean_data.keys())
    filtered_keys_list = [key for key in clean_keys_list if clean_data.get(key, []) != []]
    print(f'vertical clean {filtered_keys_list}')
    distinct_numbers = sorted(list(set(key.split('-')[0] for key in filtered_keys_list)))

    # Province mapping
    provinsi_mapping = {
        '11': ['Aceh'],
        '51': ['Bali']
    }

    summary_data = data['vertikal_data_summary']
    sum_keys_list = list(summary_data.keys())

    horizontal_clean_data = data['horizontal_clean_data']
    horizontal_clean_keys_list = list(horizontal_clean_data.keys())
    hor_filtered_keys_list = [key for key in horizontal_clean_keys_list if horizontal_clean_data.get(key, []) != []]
    print(f'horizontal clean {hor_filtered_keys_list}')

    horizontal_raw_data = data['horizontal_raw_data']
    horizontal_raw_keys_list = list(horizontal_raw_data.keys())

    rincian_data = data['rincian_data']
    rincian_df = pd.DataFrame(rincian_data)
    html_rincian_df = rincian_df.to_html(escape=False, index=False)

    ringkasan_data = data['ringkasan_data']
    ringkasan_df = pd.DataFrame(ringkasan_data)

    def calculate_mismatch_ratio(error_count, total_count):
        # Avoid division by zero
        if total_count == 0:
            return 0  # If no data, return 0
        return (error_count / total_count) * 100

    # Define the content for each column
    definition_content = """
    ### 📊 Definisi SEKDA
    SEKDA (Statistik Ekonomi dan Keuangan Daerah) merupakan publikasi statistik Bank Indonesia bulanan yang berisi data ekonomi, keuangan, dan perbankan dengan lingkup provinsi seluruh Indonesia.
    Data/statistik yang disajikan dapat digunakan oleh pengguna untuk melihat perkembangan ekonomi, keuangan, dan perbankan di masing-masing provinsi.​​
    """

    vertical_check_content = """
    ### ✅ Vertical Check
    Fitur pengecekan konsistensi nilai agregat dengan penjumlahan nilai komponen-komponen pembentuk pada tabel secara vertikal.
    """

    horizontal_check_content = """
    ### 📈 Horizontal Check
    Fitur pengecekan konsistensi nilai tahunan dengan nilai posisi atau nilai transaksi pada komponen tabel. 
    1. **Data Posisi:** Membandingkan nilai data pada kolom tahunan dengan data dari posisi kolom akhir periode tahun tersebut (Desember). 
    2. **Data Transaksi:** Membandingkan data pada kolom tahunan dengan hasil penjumlahan nilai seluruh periode di tahun tersebut.
    """

    # Create three equal columns
    col1, col2, col3 = st.columns(3)

    # Add content to each column with styling
    # Add content to each column
    with col1:
        st.markdown(definition_content)

    with col2:
        st.markdown(vertical_check_content)

    with col3:
        st.markdown(horizontal_check_content)

    total_tabel = ringkasan_df['Total tabel'].values[0]
    correct_count = ringkasan_df['Provinsi Lolos QA'].values[0]
    error_count = ringkasan_df['Provinsi Tidak Lolos QA'].values[0]
    total_count = ringkasan_df['Total provinsi'].values[0]
    ver_error_tabel = ringkasan_df['Error Vertikal'].values[0]
    hor_error_tabel = ringkasan_df['Error Horizontal'].values[0]
    total_tabel = int(total_tabel)
    correct_count = int(correct_count)
    error_count = int(error_count)
    total_count = int(total_count)
    ver_error_tabel = int(ver_error_tabel)
    hor_error_tabel = int(hor_error_tabel)

    # Calculate mismatch ratio
    mismatch_ratio_prov = calculate_mismatch_ratio(error_count, total_count)
    mismatch_ratio_ver = calculate_mismatch_ratio(ver_error_tabel, total_tabel)
    mismatch_ratio_hor = calculate_mismatch_ratio(hor_error_tabel, total_tabel)

    col1_g, col2_g, col3_g, col4_g = st.columns((2, 2, 2, 3))

    with col1_g:
        st.markdown(
            "<p style='text-align: center;'><span style='text-align: center;font-weight: bold; text-decoration: underline;'>Rasio Konsistensi Cek Horizontal</span></p>",
            unsafe_allow_html=True)

        hor_correct_count =  total_tabel - hor_error_tabel

        # Create pie chart with mismatch (errors) and correct counts
        create_pie_chart(hor_error_tabel, hor_correct_count, "Konsisten", "Tidak Konsisten")

        # Display the mismatch ratio as a percentage
        st.markdown(
            f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{mismatch_ratio_hor:.2f}%</span> data tidak konsisten.</p>",
            unsafe_allow_html=True)

    with col2_g:
        st.markdown(
            "<p style='text-align: center;'><span style='text-align: center;font-weight: bold; text-decoration: underline;'>Rasio Konsistensi Cek Vertikal</span></p>",
            unsafe_allow_html=True)

        ver_correct_count =  total_tabel - ver_error_tabel

        # Create pie chart with mismatch (errors) and correct counts
        create_pie_chart(ver_error_tabel, ver_correct_count, "Konsisten", "Tidak Konsisten")

        # Display the mismatch ratio as a percentage
        st.markdown(
            f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{mismatch_ratio_ver:.2f}%</span> data tidak konsisten.</p>",
            unsafe_allow_html=True)

    with col3_g:
        st.markdown(
            "<p style='text-align: center;'><span style='text-align: center;font-weight: bold; text-decoration: underline;'>Rasio Provinsi Lolos dan Tidak Lolos QA</span></p>",
            unsafe_allow_html=True)

        # Create pie chart with mismatch (errors) and correct counts
        create_pie_chart(error_count, correct_count, "Lolos", "Tidak Lolos")

        # Display the mismatch ratio as a percentage
        st.markdown(
            f"<p style='text-align: center;'><span style='font-weight: bold; text-decoration: underline;'>{mismatch_ratio_prov:.2f}%</span> provinsi tidak lolos.</p>",
            unsafe_allow_html=True)

    with col4_g:
        st.markdown("<h1 style='text-align: center;'>RINGKASAN</h1>", unsafe_allow_html=True)
        st.markdown(divider_style, unsafe_allow_html=True)
        # Use an expander to show the dataframe in a dropdown-like view
        with st.expander("Lihat rincian:"):
            st.markdown(html_rincian_df, unsafe_allow_html=True)


    # Define layout with two columns
    col1, col2 = st.columns((1, 4))

    with col1:
        st.text("Ingin melakukan apa?")

        # Create a button for each distinct number, replace number with province name
        for num in distinct_numbers:
            # Get the province name from the mapping, default to num if not found
            province_name = provinsi_mapping.get(num, [num])[0]

            # Create an expander (dropdown) for each province
            with st.expander(f"{province_name}"):
                # Inside the expander, display buttons for matching keys from filtered_keys_list
                matching_keys = [key for key in filtered_keys_list if key.startswith(num)]
                for table in matching_keys:
                    table_label = table.split('-')[1]

                    # Use a unique key for each button by appending the full table name
                    if st.button(f"{table_label}", key=f"button_{table}"):
                        st.session_state.selected_table = table

    with col2:
        if 'selected_table' in st.session_state:
            selected_number = st.session_state.selected_table
            filtered_keys = [key for key in clean_keys_list if key.startswith(selected_number)]
            for i in filtered_keys:
                df_clean = pd.DataFrame(clean_data[i])
                if df_clean is not None and not df_clean.empty and not (len(df_clean.columns) == 2 and 'Keterangan' in df_clean.columns):
                    st.markdown("<h1 class='centered-title'>VERTICAL CHECK</h1>", unsafe_allow_html=True)
                    df_summary = pd.DataFrame(summary_data[i])
                    st.markdown(divider_style, unsafe_allow_html=True)
                    kode_provinsi, tabel = i.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    i_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"

                    st.subheader(f"{i_new}")

                    display_dataframe(df_summary)

                    with st.expander("See Detail?"):
                        st.write("""
                        **Penjelasan Warna:**
                        - 🟩 : Aggregat
                        - 🟨 : Calculated
                        - 🟥 : Selisih
                        """)
                        st.dataframe(df_clean.style.apply(highlight_rows, axis=1).set_properties(
                        **{'text-align': 'center'}).set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                        ).format(precision=2))

            if selected_number in horizontal_clean_data:
                df_clean_hori = pd.DataFrame(horizontal_clean_data[selected_number])
                if df_clean_hori is not None and not df_clean_hori.empty:
                    st.markdown("<h1 class='centered-title'>HORIZONTAL CHECK</h1>", unsafe_allow_html=True)
                    kode_provinsi, tabel = selected_number.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    selected_number_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"
                    st.subheader(f"{selected_number_new}")
                    st.dataframe(
                        df_clean_hori.style.set_properties(**{'text-align': 'center'})
                            .set_table_styles([{'selector': 'th',
                                                'props': [('text-align', 'center'),
                                                          ('background-color', '#E8F6F3')]}])
                    )


        else:
            st.markdown("<h1 class='centered-title'>VERTICAL CHECK</h1>", unsafe_allow_html=True)
            for i in range(len(clean_data)):
                df_clean = pd.DataFrame(clean_data[clean_keys_list[i]])
                if df_clean is not None and not df_clean.empty and not (len(df_clean.columns) == 2 and 'Keterangan' in df_clean.columns):
                    df_summary = pd.DataFrame(summary_data[sum_keys_list[i]])
                    kode_provinsi, tabel = clean_keys_list[i].split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    inew = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"

                    st.markdown(divider_style, unsafe_allow_html=True)
                    st.subheader(f"{inew}")

                    display_dataframe(df_summary)

                    with st.expander("See Detail?"):
                        st.write("""
                        **Penjelasan Warna:**
                        - 🟩 : Aggregat
                        - 🟨 : Calculated
                        - 🟥 : Selisih
                        """)
                        st.dataframe(df_clean.style.apply(highlight_rows, axis=1).set_properties(
                        **{'text-align': 'center'}).set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                        ).format(precision=2))

            for item in horizontal_clean_keys_list:
                df_clean_hori = pd.DataFrame(horizontal_clean_data[item])
                if df_clean_hori is not None and not df_clean_hori.empty:
                    st.markdown("<h1 class='centered-title'>HORIZONTAL CHECK</h1>", unsafe_allow_html=True)
                    kode_provinsi, tabel = item.split('-')
                    nama_provinsi = provinsi_mapping.get(kode_provinsi, ['Unknown'])[0]
                    item_new = f"{nama_provinsi} ({kode_provinsi}) - Tabel {tabel}"
                    st.subheader(f"{item_new}")
                    st.dataframe(df_clean_hori.style.set_properties(**{'text-align': 'center'}).set_table_styles(
                        [{'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#E8F6F3')]}]
                    ).format(precision=2))

# Example usage of the main function
list_tahun = ['2022']  # Define list_tahun as needed
if __name__ == "__main__":
    main()
