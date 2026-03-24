import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Hassas Tablo OCR", layout="wide")
st.title("🎯 Nokta Atışı Tablo Okuyucu")

uploaded_file = st.file_uploader("PDF Formunu Yükle", type=["pdf"])

if uploaded_file:
    if st.button("TABLO YAPISINI KORUYARAK OKU"):
        with st.spinner('Tablo hücreleri hesaplanıyor...'):
            images = convert_from_bytes(uploaded_file.read())
            full_df = pd.DataFrame()

            for i, img in enumerate(images):
                # Veriyi sözlük formatında al
                d = pytesseract.image_to_data(img, lang='tur', output_type=pytesseract.Output.DICT)
                df_page = pd.DataFrame(d)
                
                # Temizlik
                df_page = df_page[df_page['conf'] > 20]
                df_page = df_page[df_page['text'].str.strip() != ""]
                
                if not df_page.empty:
                    # SATIR VE SÜTUN tespiti için koordinat yuvarlama
                    # 'top' (yükseklik) değerini 25 piksele yuvarlayarak aynı satırı buluruz
                    df_page['row_idx'] = (df_page['top'] // 25) * 25
                    # 'left' (sol mesafe) değerini 100 piksele yuvarlayarak sütunları ayırırız
                    df_page['col_idx'] = (df_page['left'] // 100) * 100
                    
                    # Aynı hücreye düşen kelimeleri birleştir
                    pivot_df = df_page.pivot_table(
                        index='row_idx', 
                        columns='col_idx', 
                        values='text', 
                        aggfunc=lambda x: " ".join(x)
                    ).reset_index(drop=True)
                    
                    full_df = pd.concat([full_df, pivot_df], ignore_index=True)

            if not full_df.empty:
                st.success("Tablo hücresel olarak ayrıştırıldı!")
                st.dataframe(full_df)

                # EXCEL ÇIKTISI
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    full_df.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 DÜZENLİ EXCELİ İNDİR",
                    data=output.getvalue(),
                    file_name="Duzenli_Tablo.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
