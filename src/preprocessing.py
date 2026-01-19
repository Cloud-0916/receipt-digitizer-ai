"""
画像前処理モジュール
レシート・帳票画像をOCRしやすい状態に変換する
"""

import cv2
import numpy as np
from typing import Tuple, Optional


class ImagePreprocessor:
    """画像前処理を行うクラス"""
    
    def __init__(self):
        """初期化"""
        pass
    
    # ============================================
    # 基本的な前処理
    # ============================================
    
    def grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        グレースケール変換
        カラー情報は文字認識に不要なため、グレースケール化する
        
        Args:
            image: 入力画像 (BGR形式)
        
        Returns:
            グレースケール画像
        """
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    
    def binarize_otsu(self, gray_image: np.ndarray) -> np.ndarray:
        """
        大津の二値化
        文字をくっきりさせる（黒文字・白背景に）
        
        Args:
            gray_image: グレースケール画像
        
        Returns:
            二値化された画像
        """
        # 大津の方法で自動的に最適な閾値を決定
        _, binary = cv2.threshold(
            gray_image, 
            0, 
            255, 
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return binary
    
    def denoise(self, image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """
        ノイズ除去
        細かいゴミや斑点を除去する
        
        Args:
            image: 入力画像
            kernel_size: フィルタサイズ（奇数である必要がある）
        
        Returns:
            ノイズ除去後の画像
        """
        return cv2.medianBlur(image, kernel_size)
    
    # ============================================
    # 応用的な前処理
    # ============================================
    
    def resize_for_ocr(
        self, 
        image: np.ndarray, 
        target_width: int = 2000
    ) -> np.ndarray:
        """
        OCRに適したサイズにリサイズ
        小さすぎる画像は拡大、大きすぎる画像は縮小
        
        Args:
            image: 入力画像
            target_width: 目標の幅（ピクセル）
        
        Returns:
            リサイズ後の画像
        """
        height, width = image.shape[:2]
        
        # 幅がtarget_widthになるように比率を計算
        if width != target_width:
            ratio = target_width / width
            new_width = target_width
            new_height = int(height * ratio)
            
            # アンチエイリアシングを考慮したリサイズ
            interpolation = cv2.INTER_AREA if ratio < 1 else cv2.INTER_CUBIC
            resized = cv2.resize(
                image, 
                (new_width, new_height), 
                interpolation=interpolation
            )
            return resized
        
        return image
    
    def adaptive_threshold(
        self, 
        gray_image: np.ndarray,
        block_size: int = 11,
        c: int = 2
    ) -> np.ndarray:
        """
        適応的二値化
        照明が不均一な画像に有効
        
        Args:
            gray_image: グレースケール画像
            block_size: 近傍領域のサイズ（奇数）
            c: 閾値から引く定数
        
        Returns:
            適応的二値化された画像
        """
        return cv2.adaptiveThreshold(
            gray_image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            block_size,
            c
        )
    
    def remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """
        影を除去
        照明が不均一な画像の影を軽減する
        
        Args:
            image: 入力画像（グレースケール）
        
        Returns:
            影除去後の画像
        """
        # モルフォロジー処理で背景を推定
        dilated = cv2.dilate(image, np.ones((7, 7), np.uint8))
        bg = cv2.medianBlur(dilated, 21)
        
        # 元画像と背景の差分を取る
        diff = 255 - cv2.absdiff(image, bg)
        
        # 正規化
        normalized = cv2.normalize(
            diff,
            None,
            alpha=0,
            beta=255,
            norm_type=cv2.NORM_MINMAX,
            dtype=cv2.CV_8UC1
        )
        
        return normalized
    
    def deskew(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        傾き補正
        画像の傾きを検出して修正する
        
        Args:
            image: 入力画像（グレースケールまたは二値化済み）
        
        Returns:
            補正後の画像, 回転角度
        """
        # エッジ検出
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # ハフ変換で直線検出
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is None:
            return image, 0.0
        
        # 角度の中央値を計算
        angles = []
        for rho, theta in lines[:, 0]:
            angle = np.degrees(theta) - 90
            # -45度から45度の範囲に限定
            if -45 < angle < 45:
                angles.append(angle)
        
        if not angles:
            return image, 0.0
        
        median_angle = np.median(angles)
        
        # 回転行列を作成
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        
        # 画像を回転
        rotated = cv2.warpAffine(
            image,
            M,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated, median_angle
    
    # ============================================
    # 統合処理パイプライン
    # ============================================
    
    def preprocess_basic(self, image: np.ndarray) -> np.ndarray:
        """
        基本的な前処理パイプライン
        
        手順:
        1. グレースケール化
        2. ノイズ除去
        3. 大津の二値化
        
        Args:
            image: 入力画像
        
        Returns:
            前処理済み画像
        """
        # ステップ1: グレースケール化
        gray = self.grayscale(image)
        
        # ステップ2: ノイズ除去
        denoised = self.denoise(gray)
        
        # ステップ3: 二値化
        binary = self.binarize_otsu(denoised)
        
        return binary
    
    def preprocess_advanced(
        self, 
        image: np.ndarray,
        apply_deskew: bool = True,
        apply_shadow_removal: bool = True
    ) -> Tuple[np.ndarray, dict]:
        """
        高度な前処理パイプライン
        影のある画像や傾いた画像に対応
        
        Args:
            image: 入力画像
            apply_deskew: 傾き補正を適用するか
            apply_shadow_removal: 影除去を適用するか
        
        Returns:
            前処理済み画像, 処理情報の辞書
        """
        info = {}
        
        # ステップ1: リサイズ
        resized = self.resize_for_ocr(image)
        
        # ステップ2: グレースケール化
        gray = self.grayscale(resized)
        
        # ステップ3: 影除去（オプション）
        if apply_shadow_removal:
            gray = self.remove_shadows(gray)
            info['shadow_removal'] = True
        
        # ステップ4: 傾き補正（オプション）
        if apply_deskew:
            gray, angle = self.deskew(gray)
            info['deskew_angle'] = angle
        
        # ステップ5: ノイズ除去
        denoised = self.denoise(gray)
        
        # ステップ6: 適応的二値化（照明ムラに強い）
        binary = self.adaptive_threshold(denoised)
        
        return binary, info


# ============================================
# ユーティリティ関数
# ============================================

def load_image(image_path: str) -> Optional[np.ndarray]:
    """
    画像ファイルを読み込む
    
    Args:
        image_path: 画像ファイルのパス
    
    Returns:
        画像データ（失敗時はNone）
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"エラー: 画像を読み込めませんでした: {image_path}")
    return image


def save_image(image: np.ndarray, output_path: str) -> bool:
    """
    画像を保存する
    
    Args:
        image: 保存する画像
        output_path: 保存先のパス
    
    Returns:
        成功したかどうか
    """
    result = cv2.imwrite(output_path, image)
    if result:
        print(f"画像を保存しました: {output_path}")
    else:
        print(f"エラー: 画像の保存に失敗しました: {output_path}")
    return result


def compare_images(original: np.ndarray, processed: np.ndarray) -> np.ndarray:
    """
    元画像と処理後の画像を横に並べて比較表示用の画像を作成
    
    Args:
        original: 元画像
        processed: 処理後の画像
    
    Returns:
        横に並べた画像
    """
    # 処理後の画像がグレースケールの場合、3チャンネルに変換
    if len(processed.shape) == 2:
        processed = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
    
    # 元画像もグレースケールの場合、3チャンネルに変換
    if len(original.shape) == 2:
        original = cv2.cvtColor(original, cv2.COLOR_GRAY2BGR)
    
    # 高さを揃える
    h1, h2 = original.shape[0], processed.shape[0]
    if h1 > h2:
        scale = h1 / h2
        processed = cv2.resize(processed, None, fx=scale, fy=scale)
    elif h2 > h1:
        scale = h2 / h1
        original = cv2.resize(original, None, fx=scale, fy=scale)
    
    # 横に連結
    combined = np.hstack([original, processed])
    return combined 
