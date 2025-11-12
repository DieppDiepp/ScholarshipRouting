"""
Script test API endpoints
Chạy file này để test các API endpoints (sau khi đã start server)
"""
import requests
import json

# Cấu hình
API_BASE_URL = "http://localhost:8000"  # Đổi thành 5000 nếu dùng Flask

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")

def test_simple_chat():
    """Test chat endpoint - câu hỏi đơn giản"""
    print("\n" + "="*60)
    print("TEST 2: Simple Chat (No Profile)")
    print("="*60)
    
    payload = {
        "query": "Học bổng nào ở Thổ Nhĩ Kỳ?",
        "profile_enabled": False
    }
    
    response = requests.post(f"{API_BASE_URL}/api/chat", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nQuery: {result['query']}")
        print(f"Intent: {result['intent']}")
        print(f"Tools used: {result['tools_used']}")
        print(f"\nAnswer:\n{result['answer']}")
    else:
        print(f"Error: {response.text}")

def test_chat_with_profile():
    """Test chat endpoint - với profile"""
    print("\n" + "="*60)
    print("TEST 3: Chat with Profile")
    print("="*60)
    
    payload = {
        "query": "Tôi nên apply học bổng nào?",
        "profile_enabled": True,
        "user_profile": {
            "age": 22,
            "gpa": 3.5,
            "current_degree": "Bachelor",
            "field_of_study": "Computer Science",
            "target_degree": "Master",
            "target_field": "Engineering",
            "language_certificates": [
                {"type": "IELTS", "score": 7.0}
            ]
        }
    }
    
    response = requests.post(f"{API_BASE_URL}/api/chat", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nQuery: {result['query']}")
        print(f"Intent: {result['intent']}")
        print(f"Has profile: {result['metadata']['has_profile']}")
        print(f"\nAnswer:\n{result['answer']}")
    else:
        print(f"Error: {response.text}")

def test_get_countries():
    """Test get countries endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Get Countries")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/api/scholarships/countries")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total countries: {result['count']}")
        print(f"Countries: {', '.join(result['countries'][:10])}...")
    else:
        print(f"Error: {response.text}")

def test_get_fields():
    """Test get fields endpoint"""
    print("\n" + "="*60)
    print("TEST 5: Get Fields")
    print("="*60)
    
    response = requests.get(f"{API_BASE_URL}/api/scholarships/fields")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Total fields: {result['count']}")
        print(f"Fields: {', '.join(result['fields'][:10])}...")
    else:
        print(f"Error: {response.text}")

def test_search_scholarships():
    """Test search scholarships endpoint"""
    print("\n" + "="*60)
    print("TEST 6: Search Scholarships")
    print("="*60)
    
    params = {
        "country": "Turkey",
        "funding": "Full"
    }
    
    response = requests.get(f"{API_BASE_URL}/api/scholarships/search", params=params)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Found: {result['count']} scholarships")
        print(f"Filters: {result['filters']}")
        
        if result['scholarships']:
            print(f"\nFirst scholarship:")
            first = result['scholarships'][0]
            print(f"  Name: {first.get('Scholarship_Name')}")
            print(f"  Country: {first.get('Country')}")
            print(f"  Funding: {first.get('Funding_Level')}")
    else:
        print(f"Error: {response.text}")

def test_get_scholarship_details():
    """Test get scholarship details endpoint"""
    print("\n" + "="*60)
    print("TEST 7: Get Scholarship Details")
    print("="*60)
    
    scholarship_name = "Turkiye Burslari (Turkey Government Scholarship)"
    
    response = requests.get(f"{API_BASE_URL}/api/scholarships/{scholarship_name}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nScholarship: {result.get('Scholarship_Name')}")
        print(f"Country: {result.get('Country')}")
        print(f"Funding: {result.get('Funding_Level')}")
        print(f"Deadline: {result.get('End_Date')}")
        print(f"URL: {result.get('Url')}")
    else:
        print(f"Error: {response.text}")

def main():
    """Chạy tất cả tests"""
    print("\n" + "#"*60)
    print("SCHOLARSHIP CHATBOT API - TEST SUITE")
    print("#"*60)
    print(f"\nAPI Base URL: {API_BASE_URL}")
    print("\nĐảm bảo server đang chạy trước khi test!")
    print("  - FastAPI: python api_fastapi.py")
    print("  - Flask: python api_flask.py")
    
    input("\nNhấn Enter để bắt đầu test...")
    
    try:
        # Chạy các tests
        test_health_check()
        input("\n[Nhấn Enter để tiếp tục...]")
        
        test_simple_chat()
        input("\n[Nhấn Enter để tiếp tục...]")
        
        test_chat_with_profile()
        input("\n[Nhấn Enter để tiếp tục...]")
        
        test_get_countries()
        input("\n[Nhấn Enter để tiếp tục...]")
        
        test_get_fields()
        input("\n[Nhấn Enter để tiếp tục...]")
        
        test_search_scholarships()
        input("\n[Nhấn Enter để tiếp tục...]")
        
        test_get_scholarship_details()
        
        print("\n" + "#"*60)
        print("✓ TẤT CẢ TESTS HOÀN THÀNH")
        print("#"*60)
        
    except requests.exceptions.ConnectionError:
        print("\n✗ LỖI: Không thể kết nối đến server!")
        print("Hãy đảm bảo server đang chạy:")
        print("  - FastAPI: python api_fastapi.py")
        print("  - Flask: python api_flask.py")
    except Exception as e:
        print(f"\n✗ LỖI: {e}")

if __name__ == "__main__":
    main()
