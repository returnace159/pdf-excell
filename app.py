import streamlit as st
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
from PIL import Image
import tempfile
import os

st.set_page_config(page_title="PDF'ten Excel'e OCR", layout="wide")
st.title("📄 PDF to Excel OCR Converter")

uploaded_file = st.file_uploader("Bir PDF dosyası yükleyin", type=["pdf"])

if uploaded_file is not None:
    with st.spinner('PDF işleniyor ve metinler okunuyor...'):
        # PDF'i geçici bir dosyaya kaydet
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        # PDF sayfalarını resme dönüştür
        images = convert_from_path(tmp_path)
        
        all_text_data = []
        
        for i, image in enumerate(images):
            # Tesseract ile Türkçe metin okuma
            text = pytesseract.image_to_string(image, lang='tur')
            lines = text.split('\n')
            for line in lines:
                if line.strip(): # Boş olmayan satırları al
                    all_text_data.append([f"Sayfa {i+1}", line.strip()])

        # Verileri DataFrame'e dök
        df = pd.DataFrame(all_text_data, columns=["Sayfa", "Metin İçeriği"])
        
        st.success("Metinler başarıyla ayrıştırıldı!")
        st.dataframe(df)

        # Excel'e dönüştür ve indirme butonu koy
        @st.cache_data
        def convert_df(df):
            return df.to_excel(index=False).encode('utf-8')

        # Excel dosyası hazırlama (pandas to_excel kullanımı)
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        st.download_button(
            label="📥 Excel Olarak İndir",
            data=output.getvalue(),
            file_name="ocr_sonuc.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Temizlik
        os.remove(tmp_path)
