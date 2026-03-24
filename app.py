import streamlit as st
import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import numpy as np
from PIL import Image
import tempfile
import os
from io import BytesIO

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Proje OCR: PDF to Excel", layout="wide")

def main():
    st.title("📂 Profesyonel PDF - Excel Dönüştürücü (OCR)")
    st.info("Demir Kural: Tablo yapısını korumaya odaklı tarama yapar.")

    # Dosya Yükleme
    uploaded_file = st.file_uploader("Bakım Formu veya Tablolu PDF Yükle", type=["pdf"])

    if uploaded_file:
        # OCR Dili Seçimi
        lang = st.selectbox("Okuma Dili Seçin:", ["tur", "eng"], index=0)
        
        if st.button("VERİLERİ AYIKLA VE EXCEL'E DÖNÜŞTÜR"):
            with st.spinner('Görsel işleniyor, bu işlem PDF sayfa sayısına göre vakit alabilir...'):
                try:
                    # PDF'i geçici dosyaya yaz
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name

                    # PDF -> Resim Dönüşümü
                    images = convert_from_path(tmp_path)
                    final_data = []

                    for i, img in enumerate(images):
                        # Tesseract ile veriyi 'data' formatında al (koordinatlı okuma için)
                        # Bu yöntem düz string okumadan daha isabetli sonuç verir
                        data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
                        
                        df_page = pd.DataFrame(data)
                        # Sadece güvenilir (conf > 0) ve boş olmayan metinleri al
                        df_page = df_page[df_page['conf'] > 0]
                        df_page = df_page[df_page['text'].str.strip() != ""]
                        
                        # Satırları (top değerine göre) gruplayarak tablo yapısını taklit et
                        # Aynı hizadaki metinleri aynı satıra toplar
                        df_page['line'] = df_page['top'].apply(lambda x: x // 10) # 10 piksellik tolerans
                        lines = df_page.groupby('line')['text'].apply(lambda x: " ".join(x)).reset_index()
                        
                        for _, row in lines.iterrows():
                            final_data.append({"Sayfa": i+1, "İçerik": row['text']})

                    # Sonuç Tablosu
                    result_df = pd.DataFrame(final_data)
                    st.success("İşlem Tamamlandı!")
                    st.dataframe(result_df, use_container_width=True)

                    # Excel İndirme İşlemi
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        result_df.to_excel(writer, index=False, sheet_name='OCR_Sonuc')
                    
                    st.download_button(
                        label="📥 EXCEL OLARAK İNDİR",
                        data=output.getvalue(),
                        file_name="OCR_Analiz_Raporu.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                    # Temizlik
                    os.remove(tmp_path)

                except Exception as e:
                    st.error(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    main()
