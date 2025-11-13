"""
Module B: Response Generator - Tạo sinh câu trả lời
Sử dụng Gemini API để tạo câu trả lời từ context đã tổng hợp
"""
import google.generativeai as genai
import threading
from config import Config
from core.models.intent import Intent, IntentType

class ResponseGenerator:
    """Bộ tạo sinh câu trả lời sử dụng Gemini API"""
    
    def __init__(self):
        """Khởi tạo Response Generator"""
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # Safety settings - giảm độ nghiêm ngặt để tránh bị block
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        # Giới hạn max_output_tokens để tránh response quá dài (đặc biệt cho static_comparison)
        max_tokens = min(Config.MAX_TOKENS, 2048)  # Giới hạn tối đa 2048 tokens
        
        # Sử dụng model chất lượng cao cho generation
        self.model = genai.GenerativeModel(
            Config.GEMINI_MODEL_GENERATION,
            generation_config={
                "temperature": Config.TEMPERATURE,
                "max_output_tokens": max_tokens,
            },
            safety_settings=safety_settings
        )
    
    def generate(self, query: str, context: str, intent: Intent) -> str:
        """
        Tạo câu trả lời từ query và context
        
        Args:
            query: Câu hỏi gốc của người dùng
            context: Context đã được tổng hợp từ các tools
            intent: Intent đã được phân loại
            
        Returns:
            Câu trả lời được tạo sinh
        """
        # Rút gọn context nếu quá dài (giới hạn ~8000 chars = ~2000 tokens để tránh response quá dài)
        max_context_length = 8000
        if len(context) > max_context_length:
            print(f"⚠ Context quá dài ({len(context)} chars), đang rút gọn...")
            context = context[:max_context_length] + "\n\n[... Context đã được rút gọn để tránh response quá dài ...]"
        
        # Tạo system prompt dựa trên intent
        system_prompt = self._get_system_prompt(intent)
        
        # Tạo full prompt
        full_prompt = f"""
{system_prompt}

{context}

=== CÂU HỎI CẦN TRẢ LỜI ===
"{query}"

=== QUY TẮC TRẢ LỜI (BẮT BUỘC - ĐỌC KỸ) ===
1. NGẮN GỌN, SÚCÍCH - Giới hạn 300-500 từ (trừ khi câu hỏi yêu cầu chi tiết)
2. TẬP TRUNG 100% vào câu hỏi - KHÔNG lan man
3. Trả lời TRỰC TIẾP ngay từ đầu - KHÔNG mở đầu dài dòng
4. Chỉ đưa thông tin LIÊN QUAN - loại bỏ thông tin thừa
5. Sử dụng bullet points ngắn gọn (mỗi bullet 1-2 câu)
6. **QUAN TRỌNG: KHÔNG LẶP LẠI thông tin - mỗi thông tin chỉ xuất hiện MỘT LẦN**
7. Nếu thiếu thông tin, nói ngắn gọn phần nào thiếu

CẤU TRÚC TRẢ LỜI:
- Câu đầu: Trả lời trực tiếp (1 câu)
- Giữa: Chi tiết quan trọng với bullet points ngắn
- Cuối: Kết luận/gợi ý (1-2 câu)

⚠️ CẢNH BÁO: Câu trả lời quá dài sẽ bị cắt ngắn. Hãy viết NGẮN GỌN và ĐÚNG TRỌNG TÂM!
"""
        
        try:
            # Gọi Gemini API với timeout 60 giây
            result = {"response": None, "error": None}
            
            def api_call():
                try:
                    result["response"] = self.model.generate_content(full_prompt)
                except Exception as e:
                    result["error"] = str(e)
            
            thread = threading.Thread(target=api_call)
            thread.daemon = True
            thread.start()
            thread.join(timeout=60)  # Timeout 60 giây cho API call
            
            # Kiểm tra timeout
            if thread.is_alive():
                print("❌ TIMEOUT: Gemini API call vượt quá 60 giây")
                return "Xin lỗi, việc tạo câu trả lời mất quá nhiều thời gian. Vui lòng thử lại."
            
            # Kiểm tra lỗi
            if result["error"]:
                print(f"✗ Lỗi khi gọi Gemini API: {result['error']}")
                return f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại sau."
            
            response = result["response"]
            
            # Kiểm tra finish_reason
            if not response or not response.candidates:
                print("✗ Không nhận được response từ Gemini")
                return "Xin lỗi, tôi không thể tạo câu trả lời lúc này. Vui lòng thử lại."
            
            candidate = response.candidates[0]
            finish_reason = candidate.finish_reason
            
            # finish_reason: 0=UNSPECIFIED, 1=STOP (OK), 2=MAX_TOKENS, 3=SAFETY, 4=RECITATION, 5=OTHER
            if finish_reason == 1:  # STOP - thành công
                answer = response.text.strip()
                print("✓ Đã tạo câu trả lời thành công")
                return answer
            
            elif finish_reason == 2:  # MAX_TOKENS - vượt quá giới hạn
                # Vẫn lấy text nếu có (không thêm thông báo vô duyên)
                if candidate.content and candidate.content.parts:
                    answer = "".join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                    print("⚠ Câu trả lời bị cắt ngắn do vượt MAX_TOKENS")
                    return answer.strip()  # Trả về luôn, không thêm thông báo
                else:
                    print("✗ Response bị block do MAX_TOKENS và không có nội dung")
                    return "Xin lỗi, câu trả lời quá dài. Vui lòng hỏi cụ thể hơn hoặc chia nhỏ câu hỏi."
            
            elif finish_reason == 3:  # SAFETY - bị chặn do an toàn
                print(f"✗ Response bị chặn do SAFETY: {candidate.safety_ratings}")
                return "Xin lỗi, câu hỏi của bạn có thể chứa nội dung nhạy cảm. Vui lòng diễn đạt lại câu hỏi."
            
            elif finish_reason == 4:  # RECITATION - vi phạm bản quyền
                print("✗ Response bị chặn do RECITATION")
                return "Xin lỗi, câu trả lời có thể vi phạm bản quyền. Vui lòng hỏi theo cách khác."
            
            else:  # OTHER hoặc UNSPECIFIED
                print(f"✗ Finish reason không xác định: {finish_reason}")
                # Thử lấy text nếu có
                if candidate.content and candidate.content.parts:
                    answer = "".join([part.text for part in candidate.content.parts if hasattr(part, 'text')])
                    if answer.strip():
                        return answer.strip()
                return "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi. Vui lòng thử lại."
            
        except Exception as e:
            print(f"✗ Lỗi khi tạo câu trả lời: {e}")
            return f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại sau."
    
    def _get_system_prompt(self, intent: Intent) -> str:
        """
        Tạo system prompt phù hợp với từng loại intent
        
        Args:
            intent: Intent đã được phân loại
            
        Returns:
            System prompt string
        """
        base_prompt = """
Bạn là một chuyên gia tư vấn học bổng quốc tế, có kiến thức sâu rộng về các chương trình học bổng 
toàn phần và bán phần trên toàn thế giới. Nhiệm vụ của bạn là cung cấp thông tin chính xác, 
hữu ích và tư vấn cá nhân hóa cho sinh viên Việt Nam muốn xin học bổng du học.
"""
        
        intent_specific_prompts = {
            IntentType.FACT_RETRIEVAL: """
NHIỆM VỤ: Trả lời TRỰC TIẾP thông tin được hỏi về học bổng.
- KHÔNG mở đầu dài dòng ("Chào bạn, với vai trò...")
- Trả lời NGAY câu hỏi (ví dụ: "Mức tài trợ của X là...")
- Chỉ đưa thông tin ĐƯỢC HỎI (nếu hỏi funding thì chỉ nói funding)
- Dùng bullet points cho dễ đọc
- Ngắn gọn, súc tích, đúng trọng tâm
""",
            IntentType.FILTERING: """
NHIỆM VỤ: Liệt kê và tóm tắt các học bổng phù hợp với tiêu chí.
- Trình bày dạng danh sách có số thứ tự
- Mỗi học bổng gồm: tên, quốc gia, mức tài trợ, deadline
- Sắp xếp theo độ phù hợp hoặc deadline
""",
            IntentType.STATIC_COMPARISON: """
NHIỆM VỤ: So sánh các học bổng một cách NGẮN GỌN và TRỌNG TÂM.
- CHỈ so sánh 4-5 tiêu chí QUAN TRỌNG NHẤT: Mức tài trợ, Điều kiện đầu vào, Deadline, Ưu điểm nổi bật
- Mỗi tiêu chí CHỈ viết 1-2 câu ngắn cho mỗi học bổng
- KHÔNG lặp lại thông tin, KHÔNG viết quá chi tiết
- Kết thúc bằng 1 câu nhận xét tổng quan (học bổng nào phù hợp với ai)
- GIỚI HẠN: Tối đa 300-400 từ cho toàn bộ câu trả lời
""",
            IntentType.GENERAL_ADVICE: """
NHIỆM VỤ: Tư vấn chung về học bổng.
- Đưa ra lời khuyên thực tế, dễ áp dụng
- Chia thành các bước cụ thể nếu có thể
- Khuyến khích và động viên người hỏi
""",
            IntentType.EXTERNAL_QA: """
NHIỆM VỤ: Trả lời câu hỏi ngoài luồng dựa trên thông tin từ Internet.
- Tổng hợp thông tin từ nhiều nguồn
- Trích dẫn nguồn khi cần
- Liên hệ với học bổng nếu có thể
""",
            IntentType.PERSONALIZED_ADVICE: """
NHIỆM VỤ: Tư vấn cá nhân hóa dựa trên profile người dùng.
- Phân tích profile và đưa ra nhận xét
- Đánh giá khả năng đỗ học bổng
- Đưa ra lời khuyên cụ thể để cải thiện hồ sơ
- Khuyến khích điểm mạnh, gợi ý khắc phục điểm yếu
""",
            IntentType.PERSONALIZED_RECOMMENDATION: """
NHIỆM VỤ: Đề xuất học bổng phù hợp với profile người dùng.
- Liệt kê 3-5 học bổng phù hợp nhất
- Giải thích tại sao phù hợp
- Đánh giá khả năng đỗ cho từng học bổng (cao/trung bình/thấp)
- Sắp xếp theo độ ưu tiên
"""
        }
        
        specific_prompt = intent_specific_prompts.get(
            intent.intent_type,
            "NHIỆM VỤ: Trả lời câu hỏi một cách hữu ích nhất có thể."
        )
        
        return base_prompt + "\n" + specific_prompt
