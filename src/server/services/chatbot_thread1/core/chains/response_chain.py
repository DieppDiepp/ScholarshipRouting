"""
Response Generation Chain - Tạo sinh câu trả lời sử dụng Langchain
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Dict, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.config import Config
from services.chatbot_thread1.core.models.intent import Intent, IntentType
from services.chatbot_thread1.core.utils.api_key_manager import get_next_gemini_key


class ResponseGenerationChain:
    """Chain để tạo sinh câu trả lời từ context"""
    
    def __init__(self):
        """Khởi tạo Response Generation Chain"""
        # Khởi tạo LLM (Gemini Flash cho generation)
        # Sử dụng API key rotation
        self.llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL_GENERATION,
            temperature=Config.TEMPERATURE,
            max_output_tokens=Config.MAX_TOKENS,  # Sử dụng đúng MAX_TOKENS từ config
            google_api_key=get_next_gemini_key(),
            timeout=60,
            # Thêm các tham số chống lặp
            top_p=0.95,  # Nucleus sampling để tăng đa dạng
            top_k=40     # Giới hạn top-k tokens
        )
        
        # Output parser
        self.parser = StrOutputParser()
    
    def _detect_language(self, query: str) -> str:
        """
        Phát hiện ngôn ngữ của query
        
        Args:
            query: Câu hỏi của người dùng
            
        Returns:
            'vi' cho tiếng Việt, 'en' cho tiếng Anh
        """
        # Đếm ký tự tiếng Việt có dấu
        vietnamese_chars = 'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
        vietnamese_chars += vietnamese_chars.upper()
        
        vietnamese_count = sum(1 for char in query if char in vietnamese_chars)
        
        # Nếu có ít nhất 3 ký tự tiếng Việt có dấu -> tiếng Việt
        if vietnamese_count >= 3:
            return 'vi'
        
        # Kiểm tra từ khóa tiếng Việt phổ biến
        vietnamese_keywords = ['học bổng', 'nộp đơn', 'xin', 'tôi', 'của', 'cho', 'là', 'có', 'được']
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in vietnamese_keywords):
            return 'vi'
        
        return 'en'
    
    def _get_system_prompt(self, intent: Intent, language: str = 'vi') -> str:
        """
        Tạo system prompt dựa trên intent và ngôn ngữ
        
        Args:
            intent: Intent đã được phân loại
            language: Ngôn ngữ ('vi', 'en', 'zh', 'ja', 'ko')
            
        Returns:
            System prompt string
        """
        # Base prompts cho từng ngôn ngữ
        base_prompts = {
            'vi': """Bạn là một chuyên gia tư vấn học bổng quốc tế, có kiến thức sâu rộng về các chương trình học bổng 
toàn phần và bán phần trên toàn thế giới. Nhiệm vụ của bạn là cung cấp thông tin chính xác, 
hữu ích và tư vấn cá nhân hóa cho sinh viên muốn xin học bổng du học.

QUAN TRỌNG: Trả lời bằng TIẾNG VIỆT.""",
            'en': """You are an international scholarship advisor with extensive knowledge of full and partial scholarship programs 
worldwide. Your mission is to provide accurate, helpful, and personalized advice to students seeking scholarships abroad.

IMPORTANT: Respond in ENGLISH.""",
            'zh': """你是一位国际奖学金顾问，对全球全额和部分奖学金项目有广泛的了解。
你的任务是为寻求出国留学奖学金的学生提供准确、有用和个性化的建议。

重要提示：用中文回答。""",
            'ja': """あなたは国際奨学金アドバイザーで、世界中の全額および部分奨学金プログラムについて幅広い知識を持っています。
あなたの使命は、留学奨学金を求める学生に正確で役立つ個別のアドバイスを提供することです。

重要：日本語で回答してください。""",
            'ko': """당신은 전 세계의 전액 및 부분 장학금 프로그램에 대한 광범위한 지식을 가진 국제 장학금 상담사입니다.
당신의 임무는 유학 장학금을 찾는 학생들에게 정확하고 유용하며 개인화된 조언을 제공하는 것입니다.

중요: 한국어로 답변하세요."""
        }
        
        base_prompt = base_prompts.get(language, base_prompts['en'])
        
        # Intent-specific prompts cho tiếng Việt
        if language == 'vi':
            intent_specific_prompts = {
                IntentType.FACT_RETRIEVAL: """
NHIỆM VỤ: Trả lời TRỰC TIẾP thông tin được hỏi về học bổng.
- KHÔNG mở đầu dài dòng
- Trả lời NGAY câu hỏi
- Chỉ đưa thông tin ĐƯỢC HỎI
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
- CHỈ so sánh 4-5 tiêu chí QUAN TRỌNG NHẤT
- Mỗi tiêu chí CHỈ viết 1-2 câu ngắn
- KHÔNG lặp lại thông tin
- Kết thúc bằng 1 câu nhận xét tổng quan
- GIỚI HẠN: Tối đa 300-400 từ
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
- Đánh giá khả năng đỗ cho từng học bổng
- Sắp xếp theo độ ưu tiên
"""
            }
        else:  # English và các ngôn ngữ khác
            intent_specific_prompts = {
                IntentType.FACT_RETRIEVAL: """
TASK: Answer DIRECTLY with the requested scholarship information.
- NO lengthy introduction
- Answer the question IMMEDIATELY
- Only provide REQUESTED information
- Use bullet points for readability
- Be concise, succinct, and on-point
""",
                IntentType.FILTERING: """
TASK: List and summarize scholarships matching the criteria.
- Present as a numbered list
- Each scholarship: name, country, funding level, deadline
- Sort by relevance or deadline
""",
                IntentType.STATIC_COMPARISON: """
TASK: Compare scholarships CONCISELY and FOCUSED.
- Compare ONLY 4-5 MOST IMPORTANT criteria
- Each criterion: write 1-2 short sentences
- DO NOT repeat information
- End with 1 overall observation
- LIMIT: Maximum 300-400 words
""",
                IntentType.GENERAL_ADVICE: """
TASK: Provide general scholarship advice.
- Give practical, actionable advice
- Break into specific steps if possible
- Encourage and motivate the asker
""",
                IntentType.EXTERNAL_QA: """
TASK: Answer off-topic questions based on Internet information.
- Synthesize information from multiple sources
- Cite sources when needed
- Relate to scholarships if possible
""",
                IntentType.PERSONALIZED_ADVICE: """
TASK: Provide personalized advice based on user profile.
- Analyze profile and provide feedback
- Assess scholarship eligibility
- Give specific advice to improve application
- Encourage strengths, suggest improvements for weaknesses
""",
                IntentType.PERSONALIZED_RECOMMENDATION: """
TASK: Recommend scholarships matching user profile.
- List 3-5 most suitable scholarships
- Explain why they match
- Assess eligibility for each scholarship
- Sort by priority
"""
            }
        
        specific_prompt = intent_specific_prompts.get(
            intent.intent_type,
            "NHIỆM VỤ: Trả lời câu hỏi một cách hữu ích nhất có thể."
        )
        
        return base_prompt + "\n" + specific_prompt
    
    def _remove_repetitions(self, text: str) -> str:
        """
        Loại bỏ các đoạn text lặp lại liên tiếp
        
        Args:
            text: Text có thể chứa lặp
            
        Returns:
            Text đã loại bỏ lặp
        """
        if not text:
            return text
        
        lines = text.split('\n')
        cleaned_lines = []
        seen_lines = set()
        consecutive_repeats = 0
        
        for line in lines:
            # Bỏ qua dòng trống
            if not line.strip():
                cleaned_lines.append(line)
                continue
            
            # Kiểm tra lặp
            line_normalized = line.strip().lower()
            if line_normalized in seen_lines:
                consecutive_repeats += 1
                # Cho phép lặp tối đa 1 lần (có thể là format hợp lệ)
                if consecutive_repeats <= 1:
                    cleaned_lines.append(line)
            else:
                consecutive_repeats = 0
                seen_lines.add(line_normalized)
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def generate(self, query: str, context: str, intent: Intent, language: str = 'vi') -> str:
        """
        Tạo câu trả lời từ query và context
        
        Args:
            query: Câu hỏi gốc của người dùng
            context: Context đã được tổng hợp từ các tools
            intent: Intent đã được phân loại
            language: Ngôn ngữ trả lời ('vi', 'en', 'zh', 'ja', 'ko')
            
        Returns:
            Câu trả lời được tạo sinh
        """
        # Rút gọn context nếu quá dài
        # Gemini Flash có context window ~32k tokens, để lại ~20k cho context, ~8k cho response
        max_context_length = 15000  # Tăng lên để có đủ thông tin
        if len(context) > max_context_length:
            print(f"⚠ Context quá dài ({len(context)} chars), đang rút gọn...")
            context = context[:max_context_length] + "\n\n[... Context đã được rút gọn ...]"
        
        # Tạo system prompt với ngôn ngữ
        system_prompt = self._get_system_prompt(intent, language)
        
        # Human prompts cho từng ngôn ngữ
        human_prompts = {
            'vi': """
{context}

=== CÂU HỎI CẦN TRẢ LỜI ===
"{query}"

=== QUY TẮC TRẢ LỜI (BẮT BUỘC) ===
1. NGẮN GỌN, SÚCÍCH - Giới hạn 300-500 từ
2. TẬP TRUNG 100% vào câu hỏi
3. Trả lời TRỰC TIẾP ngay từ đầu
4. Chỉ đưa thông tin LIÊN QUAN
5. Sử dụng bullet points ngắn gọn
6. KHÔNG LẶP LẠI thông tin
7. Nếu thiếu thông tin, nói ngắn gọn phần nào thiếu

CẤU TRÚC TRẢ LỜI:
- Câu đầu: Trả lời trực tiếp (1 câu)
- Giữa: Chi tiết quan trọng với bullet points ngắn
- Cuối: Kết luận/gợi ý (1-2 câu)
""",
            'en': """
{context}

=== QUESTION TO ANSWER ===
"{query}"

=== ANSWER RULES (MANDATORY) ===
1. BE CONCISE - Limit 300-500 words
2. FOCUS 100% on the question
3. Answer DIRECTLY from the start
4. Only provide RELEVANT information
5. Use concise bullet points
6. DO NOT REPEAT information
7. If information is missing, briefly state what's missing

ANSWER STRUCTURE:
- First sentence: Direct answer (1 sentence)
- Middle: Important details with brief bullet points
- End: Conclusion/suggestion (1-2 sentences)
"""
        }
        
        # Lấy human prompt theo ngôn ngữ (fallback sang English)
        human_prompt = human_prompts.get(language, human_prompts['en'])
        
        # Tạo prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", human_prompt)
        ])
        
        # Tạo chain
        chain = prompt | self.llm | self.parser
        
        try:
            # Invoke chain với stop sequences
            answer = chain.invoke({
                "query": query,
                "context": context
            })
            
            # Post-processing: Loại bỏ text lặp lại
            answer = self._remove_repetitions(answer)
            
            print("✓ Đã tạo câu trả lời thành công")
            return answer.strip()
            
        except Exception as e:
            print(f"✗ Lỗi khi tạo câu trả lời: {e}")
            return f"Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn. Vui lòng thử lại sau."
