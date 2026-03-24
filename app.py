import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Korkmaz Form Analiz v5", layout="wide")
st.title("🔬 Form Yerleşim Analizörü")

# Yan menüden hassasiyet ayarları
st.sidebar.header("⚙️ Ayarlar (İnce Ayar)")
row_threshold = st.sidebar.slider("Satır Birleştirme Hassasiyeti (Yüksekse daha çok satır birleşir)", 10, 50, 25)
col_threshold = st.sidebar.slider("Sütun Genişliği (Düşükse daha çok sütun oluşur)", 50, 200, 120)

uploaded_file = st.file_uploader("PDF Formunu Yükle", type=["pdf"])

if uploaded_file:
    if st.button("FORMU YENİDEN ANALİZ ET"):
        with st.spinner('Piksel hesaplamaları yapılıyor...'):
            images = convert_from_bytes(uploaded_file.read())
            all_pages_df = []

            for i, img in enumerate(images):
                d = pytesseract.image_to_data(img, lang='tur', output_type=pytesseract.Output.DICT)
                df_page = pd.DataFrame(d)
                
                # Sadece güvenilir metinleri filtrele
                df_page = df_page[df_page['conf'] > 15]
                df_page = df_page[df_page['text'].str.strip() != ""]
                
                if not df_page.empty:
                    # Dinamik gruplama
                    df_page['row_group'] = (df_page['top'] // row_threshold) * row_threshold
                    df_page['col_group'] = (df_page['left'] // col_threshold) * col_threshold
                    
                    # Pivot Table ile ızgara yapısı kur
                    pivot = df_page.pivot_table(
                        index='row_group', 
                        columns='col_group', 
                        values='text', 
                        aggfunc=lambda x: " ".join(list(x))
                    ).sort_index()
                    
                    all_pages_df.append(pivot)

            if all_pages_df:
                final_df = pd.concat(all_pages_df, axis=0)
                st.success("Analiz bitti! Aşağıdaki tabloyu kontrol et.")
                st.dataframe(final_df)

                # Excel'e aktar
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    final_df.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 YENİ EXCEL'İ İNDİR",
                    data=output.getvalue(),
                    file_name="Korkmaz_Form_Analiz.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
