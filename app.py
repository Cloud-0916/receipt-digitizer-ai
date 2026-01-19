import streamlit as st
from PIL import Image
import io
import json
import pandas as pd
from preprocessing import preprocess_image
from ocr_engine import extract_text
from llm_parser import parse_receipt
import numpy as np

st.set_page_config(page_title="レシートデジタル化AI", layout="wide")

st.title("🧾 レシートデジタル化AI")
st.write("レシート画像をアップロードすると、AIが自動で構造化データに変換します。")

# ファイルアップロード
uploaded_file = st.file_uploader("レシート画像をアップロード", type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    # 画像を読み込み
    image = Image.open(uploaded_file)
    image_np = np.array(image)
    
    # 2カラムレイアウト
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📷 元画像")
        st.image(image, use_column_width=True)
    
    with col2:
        st.subheader("🔧 処理済み画像")
        # 前処理
        processed = preprocess_image(image_np)
        st.image(processed, use_column_width=True)
    
    # OCR & LLM処理
    if st.button("🚀 データ抽出を実行"):
        with st.spinner("処理中..."):
            # OCR実行
            ocr_text = extract_text(processed)
            
            st.subheader("📝 OCR結果")
            st.text_area("抽出されたテキスト", ocr_text, height=150)
            
            # LLMで構造化
            try:
                result = parse_receipt(ocr_text)
                
                st.subheader("✅ 構造化データ")
                st.json(result)
                
                # CSV出力用のデータ作成
                if result.get("items"):
                    df = pd.DataFrame(result["items"])
                    df["store_name"] = result.get("store_name")
                    df["date"] = result.get("date")
                    df["total"] = result.get("total")
                    
                    st.subheader("📊 テーブル表示")
                    st.dataframe(df)
                    
                    # CSVダウンロード
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 CSVダウンロード",
                        data=csv,
                        file_name="receipt_data.csv",
                        mime="text/csv"
                    )
                else:
                    # itemsがない場合は基本情報のみ
                    df = pd.DataFrame([{
                        "store_name": result.get("store_name"),
                        "date": result.get("date"),
                        "total": result.get("total")
                    }])
                    st.dataframe(df)
                    
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 CSVダウンロード",
                        data=csv,
                        file_name="receipt_data.csv",
                        mime="text/csv"
                    )
                    
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
