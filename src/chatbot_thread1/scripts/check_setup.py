"""
Script kiểm tra setup và cấu hình
Chạy file này để đảm bảo mọi thứ đã sẵn sàng
"""
import sys
from pathlib import Path

def check_python_version():
    """Kiểm tra Python version"""
    print("🔍 Kiểm tra Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Cần >= 3.8)")
        return False

def check_dependencies():
    """Kiểm tra dependencies đã cài đặt chưa"""
    print("\n🔍 Kiểm tra dependencies...")
    required = [
        'google.generativeai',
        'tavily',
        'chromadb',
        'pydantic',
        'dotenv'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (chưa cài đặt)")
            missing.append(package)
    
    if missing:
        print(f"\n   ⚠️  Cài đặt: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Kiểm tra file .env"""
    print("\n🔍 Kiểm tra file .env...")
    # Đường dẫn đến thư mục gốc (chatbot_thread1)
    root_dir = Path(__file__).parent.parent
    env_file = root_dir / ".env"
    
    if not env_file.exists():
        print("   ❌ File .env không tồn tại")
        print("   ⚠️  Tạo file .env từ .env.example")
        return False
    
    print(f"   ✅ File .env tồn tại: {env_file}")
    return True

def check_api_keys():
    """Kiểm tra API keys"""
    print("\n🔍 Kiểm tra API keys...")
    
    try:
        # Thêm root directory vào sys.path
        root_dir = Path(__file__).parent.parent
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))
        from config import Config
        
        # Check Gemini API
        if Config.GEMINI_API_KEY and Config.GEMINI_API_KEY != "your_gemini_api_key_here":
            print(f"   ✅ GEMINI_API_KEY: {Config.GEMINI_API_KEY[:20]}...")
            gemini_ok = True
        else:
            print("   ❌ GEMINI_API_KEY chưa được cấu hình")
            gemini_ok = False
        
        # Check Tavily API
        if Config.TAVILY_API_KEY and Config.TAVILY_API_KEY != "your_tavily_api_key_here":
            print(f"   ✅ TAVILY_API_KEY: {Config.TAVILY_API_KEY[:20]}...")
            tavily_ok = True
        else:
            print("   ❌ TAVILY_API_KEY chưa được cấu hình")
            print("   ⚠️  Lấy tại: https://tavily.com/")
            tavily_ok = False
        
        return gemini_ok and tavily_ok
        
    except Exception as e:
        print(f"   ❌ Lỗi khi load config: {e}")
        return False

def check_data_file():
    """Kiểm tra file dữ liệu"""
    print("\n🔍 Kiểm tra file dữ liệu...")
    
    try:
        # Thêm root directory vào sys.path để import được config
        root_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(root_dir))
        from config import Config
        data_path = root_dir / Config.DATA_PATH
        
        if data_path.exists():
            size_mb = data_path.stat().st_size / (1024 * 1024)
            print(f"   ✅ File dữ liệu tồn tại: {data_path}")
            print(f"      Kích thước: {size_mb:.2f} MB")
            return True
        else:
            print(f"   ❌ File dữ liệu không tồn tại: {data_path}")
            print(f"   ⚠️  Cập nhật DATA_PATH trong .env")
            return False
            
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
        return False

def check_vector_db():
    """Kiểm tra Vector DB"""
    print("\n🔍 Kiểm tra Vector Database...")
    
    try:
        root_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(root_dir))
        from config import Config
        vector_db_path = root_dir / Config.VECTOR_DB_PATH
        
        if vector_db_path.exists():
            print(f"   ✅ Vector DB đã được tạo: {vector_db_path}")
            print("      (Không cần index lại)")
        else:
            print(f"   ⚠️  Vector DB chưa được tạo: {vector_db_path}")
            print("      (Sẽ tự động tạo khi chạy lần đầu)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
        return False

def test_gemini_connection():
    """Test kết nối Gemini API"""
    print("\n🔍 Test kết nối Gemini API...")
    
    try:
        import google.generativeai as genai
        # Thêm root directory vào sys.path
        root_dir = Path(__file__).parent.parent
        if str(root_dir) not in sys.path:
            sys.path.insert(0, str(root_dir))
        from config import Config
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel(Config.GEMINI_MODEL)
        
        response = model.generate_content("Hello")
        
        if response.text:
            print("   ✅ Gemini API hoạt động bình thường")
            return True
        else:
            print("   ❌ Gemini API không trả về response")
            return False
            
    except Exception as e:
        print(f"   ❌ Lỗi kết nối Gemini: {e}")
        print("   ⚠️  Kiểm tra API key hoặc kết nối Internet")
        return False

def main():
    """Chạy tất cả checks"""
    print("=" * 60)
    print("KIỂM TRA SETUP - CHATBOT THREAD 1")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("File .env", check_env_file),
        ("API Keys", check_api_keys),
        ("File dữ liệu", check_data_file),
        ("Vector Database", check_vector_db),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Lỗi khi kiểm tra {name}: {e}")
            results.append((name, False))
    
    # Test Gemini nếu API key OK
    if results[3][1]:  # API Keys check passed
        try:
            gemini_result = test_gemini_connection()
            results.append(("Gemini Connection", gemini_result))
        except:
            pass
    
    # Tổng kết
    print("\n" + "=" * 60)
    print("KẾT QUẢ KIỂM TRA")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nĐạt: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 TẤT CẢ KIỂM TRA ĐỀU PASS!")
        print("✅ Bạn có thể chạy chatbot ngay:")
        print("   python main.py")
    else:
        print("\n⚠️  CÓ MỘT SỐ VẤN ĐỀ CẦN KHẮC PHỤC")
        print("📖 Xem SETUP_GUIDE.md để biết chi tiết")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
