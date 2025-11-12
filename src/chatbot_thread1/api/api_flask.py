"""
Flask Server cho Scholarship Chatbot (Backup option)
Cung cấp REST API endpoints để tương tác với chatbot
"""
import sys
from pathlib import Path

# Thêm thư mục cha vào Python path để import được các module
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify
from flask_cors import CORS
from main import ScholarshipChatbot
from core.utils.data_loader import DataLoader

# Khởi tạo Flask app
app = Flask(__name__)
CORS(app)

# Khởi tạo chatbot và data loader
chatbot = ScholarshipChatbot()
data_loader = DataLoader()

@app.route("/", methods=["GET"])
def root():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Scholarship Chatbot API is running (Flask)",
        "version": "1.0.0"
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Chat endpoint - Gửi câu hỏi và nhận câu trả lời
    """
    try:
        data = request.get_json()
        
        query = data.get("query")
        profile_enabled = data.get("profile_enabled", False)
        user_profile = data.get("user_profile")
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        result = chatbot.chat(
            query=query,
            profile_enabled=profile_enabled,
            user_profile=user_profile
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/scholarships/countries", methods=["GET"])
def get_countries():
    """Lấy danh sách tất cả các quốc gia có học bổng"""
    try:
        countries = data_loader.get_countries()
        return jsonify({
            "countries": countries,
            "count": len(countries)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/scholarships/fields", methods=["GET"])
def get_fields():
    """Lấy danh sách tất cả các ngành học"""
    try:
        fields = data_loader.get_fields()
        return jsonify({
            "fields": fields,
            "count": len(fields)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/scholarships/search", methods=["GET"])
def search_scholarships():
    """
    Tìm kiếm học bổng theo các tiêu chí
    
    Query params:
        - country: Quốc gia
        - field: Ngành học
        - degree: Bậc học (Bachelor, Master, PhD)
        - funding: Mức tài trợ (Full, Partial)
    """
    try:
        filters = {}
        
        country = request.args.get("country")
        field = request.args.get("field")
        degree = request.args.get("degree")
        funding = request.args.get("funding")
        
        if country:
            filters["Country"] = country
        if field:
            filters["Eligible_Fields"] = field
        if degree:
            filters["Required_Degree"] = degree
        if funding:
            filters["Funding_Level"] = funding
        
        results = data_loader.filter_scholarships(filters)
        
        return jsonify({
            "scholarships": results,
            "count": len(results),
            "filters": filters
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/scholarships/<scholarship_name>", methods=["GET"])
def get_scholarship_details(scholarship_name):
    """Lấy thông tin chi tiết của một học bổng"""
    try:
        scholarship = data_loader.get_scholarship_by_name(scholarship_name)
        
        if not scholarship:
            return jsonify({
                "error": f"Scholarship '{scholarship_name}' not found"
            }), 404
        
        return jsonify(scholarship)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Starting Flask Server")
    print("="*60)
    print("📍 URL: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
