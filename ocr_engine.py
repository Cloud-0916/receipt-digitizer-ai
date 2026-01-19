import easyocr
from preprocessing import load_and_preprocess
import os

# EasyOCRリーダーを初期化（初回は言語モデルをダウンロード）
reader = easyocr.Reader(['ja', 'en'])

def extract_text(image):
    """
    画像からテキストを抽出
    
    Args:
        image: 前処理済み画像
    
    Returns:
        text: 抽出されたテキスト
    """
    results = reader.readtext(image)
    # 認識結果からテキスト部分のみ抽出
    text_lines = [result[1] for result in results]
    return '\n'.join(text_lines)


def process_receipt(image_path):
    """
    レシート画像を読み込み、テキストを抽出
    
    Args:
        image_path: 画像ファイルのパス
    
    Returns:
        text: 抽出されたテキスト
    """
    original, processed = load_and_preprocess(image_path)
    text = extract_text(processed)
    return text


# テスト実行用
if __name__ == "__main__":
    input_dir = "data/raw"
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)
            
            print(f"\n{'='*50}")
            print(f"ファイル: {filename}")
            print('='*50)
            
            try:
                text = process_receipt(image_path)
                print(text)
            except Exception as e:
                print(f"エラー: {e}")