"""
Language Detector - Phát hiện ngôn ngữ của query một cách đơn giản và nhanh
Sử dụng pattern matching trước, fallback sang Gemini nếu cần
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
import os
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.chatbot_thread1.config import Config
from services.chatbot_thread1.core.utils.api_key_manager import get_next_gemini_key


class LanguageDetector:
    """
    Phát hiện ngôn ngữ của query một cách đơn giản và nhanh
    Sử dụng pattern matching trước, fallback sang Gemini nếu cần
    """
    
    # Supported languages
    SUPPORTED_LANGUAGES = {
        'vi': 'Vietnamese',
        'en': 'English',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean'
    }
    
    def __init__(self):
        """Khởi tạo detector với Gemini flash-lite (chỉ dùng khi cần)"""
        self.llm = None  # Lazy initialization
    
    def detect(self, text: str) -> str:
        """
        Phát hiện ngôn ngữ của text
        
        Args:
            text: Text cần phát hiện
            
        Returns:
            Language code: 'vi', 'en', 'zh', 'ja', 'ko'
        """
        if not text or len(text.strip()) < 3:
            return 'en'
        
        # Method 1: Pattern matching (nhanh nhất, không tốn API)
        lang = self._detect_by_pattern(text)
        if lang:
            print(f"  🌐 Detected language: {lang} ({self.get_language_name(lang)})")
            return lang
        
        # Method 2: Gemini flash-lite (fallback, chỉ khi cần)
        try:
            if self.llm is None:
                self._init_llm()
            
            detected = self.chain.invoke({"text": text[:200]}).strip().lower()
            if detected in self.SUPPORTED_LANGUAGES:
                print(f"  🌐 Detected language (via LLM): {detected} ({self.get_language_name(detected)})")
                return detected
        except Exception as e:
            print(f"  ⚠ Language detection error: {e}")
        
        # Default: English
        print(f"  🌐 Detected language: en (English) [default]")
        return 'en'
    
    def _init_llm(self):
        """Lazy initialization của LLM"""
        # Sử dụng API key rotation
        self.llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL_CLASSIFICATION,  # gemini-2.5-flash-lite
            temperature=0.0,
            google_api_key=get_next_gemini_key(),
            timeout=10
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """Detect the language of the text. Return ONLY the language code.
Supported codes: vi (Vietnamese), en (English), zh (Chinese), ja (Japanese), ko (Korean)
Return 'en' if unsure."""),
            ("human", "{text}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def _detect_by_pattern(self, text: str) -> str:
        """
        Phát hiện ngôn ngữ bằng pattern matching
        
        Args:
            text: Text cần phát hiện
            
        Returns:
            Language code hoặc None nếu không chắc chắn
        """
        # Vietnamese: có dấu đặc trưng
        vietnamese_chars = 'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ'
        vietnamese_chars += vietnamese_chars.upper()
        vietnamese_count = sum(1 for char in text if char in vietnamese_chars)
        if vietnamese_count >= 2:
            return 'vi'
        
        # Chinese: có chữ Hán
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
        if len(chinese_pattern.findall(text)) >= 3:
            return 'zh'
        
        # Japanese: có Hiragana hoặc Katakana
        japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff]')
        if len(japanese_pattern.findall(text)) >= 2:
            return 'ja'
        
        # Korean: có Hangul
        korean_pattern = re.compile(r'[\uac00-\ud7af]')
        if len(korean_pattern.findall(text)) >= 2:
            return 'ko'
        
        # English: chỉ có ASCII và không có dấu đặc biệt
        if text.isascii() and any(c.isalpha() for c in text):
            return 'en'
        
        return None
    
    def get_language_name(self, code: str) -> str:
        """Lấy tên đầy đủ của ngôn ngữ"""
        return self.SUPPORTED_LANGUAGES.get(code, 'English')
