"""
Script để liệt kê các Gemini models có sẵn với API key hiện tại
"""
import sys
import os

# Thêm parent directory vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
from config import Config

def list_available_models():
    """Liệt kê tất cả models có sẵn"""
    try:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        print("🔍 Đang kiểm tra các models có sẵn...\n")
        print("="*60)
        
        models = genai.list_models()
        
        generation_models = []
        for model in models:
            # Chỉ lấy models hỗ trợ generateContent
            if 'generateContent' in model.supported_generation_methods:
                generation_models.append(model)
                print(f"✓ {model.name}")
                print(f"  Display Name: {model.display_name}")
                print(f"  Description: {model.description}")
                print(f"  Supported methods: {model.supported_generation_methods}")
                print("-"*60)
        
        print(f"\n📊 Tổng cộng: {len(generation_models)} models hỗ trợ generateContent")
        
        if generation_models:
            print("\n💡 Gợi ý sử dụng:")
            print("   Thêm vào .env file:")
            print(f"   GEMINI_MODEL_CLASSIFICATION={generation_models[0].name}")
            print(f"   GEMINI_MODEL_GENERATION={generation_models[0].name}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        print("\n💡 Kiểm tra:")
        print("   1. API key có đúng không?")
        print("   2. API key có được kích hoạt chưa?")
        print("   3. Có kết nối Internet không?")

if __name__ == "__main__":
    list_available_models()
