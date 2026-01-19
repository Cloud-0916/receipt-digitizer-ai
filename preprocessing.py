import cv2
import numpy as np
import os

def preprocess_image(image):
    """
    OCR精度向上のための画像前処理
    
    Args:
        image: OpenCVで読み込んだ画像（BGR形式）
    
    Returns:
        binary: 前処理済み画像（二値化済み）
    """
    # 1. グレースケール変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 2. ノイズ除去
    denoised = cv2.medianBlur(gray, 3)
    
    # 3. 適応的二値化（影や照明ムラに強い）
    binary = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,  # ブロックサイズ（奇数）
        2    # 定数C
    )
    
    return binary


def load_and_preprocess(image_path):
    """
    画像を読み込んで前処理を実行
    
    Args:
        image_path: 画像ファイルのパス
    
    Returns:
        original: 元画像
        processed: 前処理済み画像
    """
    # 日本語パスに対応するため、np.fromfileを使用
    image_array = np.fromfile(image_path, dtype=np.uint8)
    original = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    if original is None:
        raise ValueError(f"画像を読み込めませんでした: {image_path}")
    
    processed = preprocess_image(original)
    
    return original, processed


def save_processed_image(image, output_path):
    """
    処理済み画像を保存
    
    Args:
        image: 保存する画像
        output_path: 出力先パス
    """
    # 日本語パスに対応
    _, encoded = cv2.imencode('.png', image)
    encoded.tofile(output_path)


# テスト実行用
if __name__ == "__main__":
    # 入出力フォルダの設定
    input_dir = "data/raw"
    output_dir = "data/processed"
    
    # 出力フォルダがなければ作成
    os.makedirs(output_dir, exist_ok=True)
    
    # rawフォルダ内の画像を処理
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"processed_{filename}")
            
            print(f"処理中: {filename}")
            
            try:
                original, processed = load_and_preprocess(input_path)
                save_processed_image(processed, output_path)
                print(f"  → 保存完了: {output_path}")
            except Exception as e:
                print(f"  → エラー: {e}")
    
    print("\n全ての画像処理が完了しました！")