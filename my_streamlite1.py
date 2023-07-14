#!/usr/bin/env python
# coding: utf-8

# In[2]:


import streamlit as st
import pandas as pd 
import numpy as np 

option = st.sidebar.selectbox(
    'Silakan pilih:',
    ('Home','Dataframe')
)

if option == 'Home' or option == '':
    st.write("""# Halaman Utama""") #menampilkan halaman utama
elif option == 'Dataframe':
    st.write("""## Dataframe""") #menampilkan judul halaman dataframe

    #membuat dataframe dengan pandas yang terdiri dari 2 kolom dan 4 baris data
    # df = pd.DataFrame({
    #     'Column 1':[1,2,3,4],
    #     'Column 2':[10,12,14,16]
    # })
    df = pd.read_csv("E:\Capstone Web Service\Cheating_Detec\dataset\labels.csv")
    df #menampilkan dataframe

    st.write("""## Draw Charts""") #menampilkan judul halaman 

    #membuat variabel chart data yang berisi data dari dataframe
    #data berupa angka acak yang di-generate menggunakan numpy
    #data terdiri dari 2 kolom dan 20 baris
    tidak_mencontek = df[(df['label_name']=='tidak_mencontek')].count()['label_name']
    mencontek = df[(df['label_name']=='mencontek')].count()['label_name']
    label = df['label_name'].count()
    chart_data = pd.DataFrame(
        df, columns=['label_name']
    )
    persentase = tidak_mencontek / label * 100
    data = {
        'Tidak Mencontek': [tidak_mencontek],
        'Mencontek' : [mencontek],
        'persentase': [persentase]
    }
    table = pd.DataFrame(data, index=['Jumlah Data'])
    #menampilkan data dalam bentuk chart
    chart_data2 = order=chart_data['label_name'].value_counts().index[:3]
    st.bar_chart(table)
    #data dalam bentuk tabel
    # chart_data2
    table
    if persentase < 90:
        st.write ("Mohon Maaf, Anda Terdeteksi Mencontek")
    else:
        st.write ("Selamat Anda Tidak Terdeteksi Mencontek")

