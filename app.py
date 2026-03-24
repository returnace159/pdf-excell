import streamlit as st
import pytesseract
from pdf2image import convert_from_bytes
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Korkmaz OCR v3", layout="wide")
st.title("📄 Akıllı Form Okuyucu (OCR Modu)")

uploaded_file = st.file_uploader("PDF Formunu Yükle", type=["pdf"])

if uploaded_file:
    if st.button("FORMU ANALİZ ET"):
        with st.spinner('Resimler taranıyor ve metinler koordine ediliyor...'):
            try:
                # PDF'i resme çevir
                images = convert_from_bytes(uploaded_file.read())
                all_data = []

                for i, img in enumerate(images):
                    # Tesseract ile her kelimenin yerini (koordinatını) bul
                    d = pytesseract.image_to_data(img, lang='tur', output_type=pytesseract.Output.DICT)
                    df_tmp = pd.DataFrame(d)
                    
                    # Sadece güvenilir ve boş olmayan metinleri al
                    df_tmp = df_tmp[df_tmp['conf'] > 30]
                    df_tmp = df_tmp[df_tmp['text'].str.strip() != ""]
                    
                    if not df_tmp.empty:
                        # Satırları (y koordinatına göre) grupla (20 piksellik tolerans)
                        df_tmp['line'] = df_tmp['top'].apply(lambda x: x // 20)
                        
                        # Her satırı kendi içinde soldan sağa (left koordinatı) diz
                        lines = df_tmp.sort_values(['line', 'left']).groupby('line')
                        
                        for _, line_df in lines:
                            text_line = " | ".join(line_df['text'].tolist())
                            all_data.append({"Sayfa": i+1, "İçerik": text_line})

                if all_data:
                    final_df = pd.DataFrame(all_data)
                    st.success("Form başarıyla okundu!")
                    st.dataframe(final_df, use_container_width=True)

                    # EXCEL OLUŞTURMA
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        final_df.to_excel(writer, index=False, sheet_name='OCR_Sonuc')
                    
                    st.download_button(
                        label="📥 EXCELİ İNDİR",
                        data=output.getvalue(),
                        file_name="Form_OCR_Ciktisi.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("PDF içinde okunabilir metin bulunamadı.")
            
            except Exception as e:
                st.error(f"Hata oluştu: {e}. Lütfen 'Manage App' kısmından logları kontrol et.")
