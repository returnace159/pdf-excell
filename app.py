import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from io import BytesIO
import re

st.title("PDF → Excel Converter")

uploaded_file = st.file_uploader("PDF dosyasını yükle", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    all_text = []

    # Her sayfanın metnini oku
    for page in reader.pages:
        text = page.extract_text()
        if text:
            lines = text.split("\n")
            # Illegal karakterleri temizle
            clean_lines = [re.sub(r'[\x00-\x1F]', '', line) for line in lines]
            all_text.extend(clean_lines)

    df = pd.DataFrame(all_text, columns=["Satır"])

    output = BytesIO()
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    st.download_button(
        label="Excel olarak indir",
        data=output,
        file_name="output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.info("Not: Bu basit sürüm sadece metin tabanlı PDF'ler için çalışır. Illegal karakterler temizlendi.")
