import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Korkmaz OCR v2", layout="wide")
st.title("📊 Akıllı Tablo Ayıklayıcı (Excel Formatlı)")

uploaded_file = st.file_uploader("PDF Formunu Yükle", type=["pdf"])

if uploaded_file:
    if st.button("TABLOYU YAKALA"):
        with st.spinner('Tablo çizgileri analiz ediliyor...'):
            all_tables = []
            
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    # extract_table metodu çizgileri takip eder, kayma yapmaz.
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        all_tables.append(df)
            
            if all_tables:
                final_df = pd.concat(all_tables, ignore_index=True)
                
                # Sütun isimlerini temizle (Boşlukları kaldır)
                final_df.columns = [str(c).replace('\n', ' ') for c in final_df.columns]
                
                st.success("Tablo Yapısı Korunarak Okundu!")
                st.dataframe(final_df) # Ekranda tablo gibi gösterir

                # EXCEL OLUŞTURMA
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    final_df.to_excel(writer, index=False, sheet_name='Bakim_Formu')
                
                st.download_button(
                    label="📥 BURAYA TIKLA VE EXCELİ İNDİR",
                    data=output.getvalue(),
                    file_name="Bakim_Formu_Duzenli.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error("PDF içinde belirgin bir tablo çizgisi bulunamadı.")
