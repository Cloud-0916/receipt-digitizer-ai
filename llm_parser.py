import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# .envからAPIキーを読み込み
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# モデルを初期化
model = genai.GenerativeModel('gemini-2.0-flash')

def parse_receipt(ocr_text):
    """
    OCRテキストをLLMで構造化データに変換
    
    Args:
        ocr_text: OCRで読み取ったテキスト
    
    Returns:
        dict: 構造化されたレシートデータ
    """
    prompt = f"""以下のテキストはレシートをOCRした結果です。誤字脱字が含まれる可能性があります。
このテキストから情報を抽出し、以下のJSON形式のみを出力してください。
余計な解説は不要です。不明な場合はnullを入れてください。

出力形式:
{{
    "store_name": "店舗名",
    "date": "YYYY-MM-DD",
    "items": [
        {{"name": "商品名", "quantity": 数量, "price": 金額}}
    ],
    "total": 合計金額
}}

OCRテキスト:
{ocr_text}
"""
    
    response = model.generate_content(prompt)
    
    # レスポンスからJSONを抽出
    response_text = response.text.strip()
    
    # ```json ... ``` の形式で返ってきた場合の処理
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    return json.loads(response_text)


# テスト実行用
if __name__ == "__main__":
    from ocr_engine import process_receipt
    
    input_dir = "data/raw"
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)
            
            print(f"\n{'='*50}")
            print(f"ファイル: {filename}")
            print('='*50)
            
            try:
                # OCR実行
                ocr_text = process_receipt(image_path)
                print("【OCR結果】")
                print(ocr_text[:200] + "..." if len(ocr_text) > 200 else ocr_text)
                
                # LLMで構造化
                print("\n【構造化結果】")
                result = parse_receipt(ocr_text)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
            except Exception as e:
                print(f"エラー: {e}")

from groq import Groq
from dotenv import load_dotenv
import os
import json

# .envからAPIキーを読み込み
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_receipt(ocr_text):
    """
    OCRテキストをLLMで構造化データに変換
    """
    prompt = f"""以下のテキストはレシートをOCRした結果です。誤字脱字が含まれる可能性があります。
このテキストから情報を抽出し、以下のJSON形式のみを出力してください。
余計な解説は不要です。不明な場合はnullを入れてください。

出力形式:
{{
    "store_name": "店舗名",
    "date": "YYYY-MM-DD",
    "items": [
        {{"name": "商品名", "quantity": 数量, "price": 金額}}
    ],
    "total": 合計金額
}}

OCRテキスト:
{ocr_text}
"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    
    response_text = response.choices[0].message.content.strip()
    
    # ```json ... ``` の形式で返ってきた場合の処理
    if response_text.startswith("```"):
        response_text = response_text.split("```")[1]
        if response_text.startswith("json"):
            response_text = response_text[4:]
        response_text = response_text.strip()
    
    return json.loads(response_text)


# テスト実行用
if __name__ == "__main__":
    from ocr_engine import process_receipt
    
    input_dir = "data/raw"
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)
            
            print(f"\n{'='*50}")
            print(f"ファイル: {filename}")
            print('='*50)
            
            try:
                # OCR実行
                ocr_text = process_receipt(image_path)
                print("【OCR結果】")
                print(ocr_text[:200] + "..." if len(ocr_text) > 200 else ocr_text)
                
                # LLMで構造化
                print("\n【構造化結果】")
                result = parse_receipt(ocr_text)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                
            except Exception as e:
                print(f"エラー: {e}")