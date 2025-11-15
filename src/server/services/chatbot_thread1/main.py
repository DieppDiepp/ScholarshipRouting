"""
Main Module - Chatbot Thread 1 (Refactored với Langchain)
Hệ thống chatbot tư vấn học bổng với Intent Routing và Multi-Tool Retrieval
"""
import os
import sys
import threading
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Add parent directories to path để có thể import
current_dir = os.path.dirname(os.path.abspath(__file__))
# current_dir = .../chatbot_thread1
# parent = .../services
# parent.parent = .../server
server_dir = os.path.dirname(os.path.dirname(current_dir))
if server_dir not in sys.path:
    sys.path.insert(0, server_dir)

from services.chatbot_thread1.config import Config
from services.chatbot_thread1.core.agents.scholarship_agent import ScholarshipAgent

# Setup logging (giống thread2)
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE_PATH = BASE_DIR / "chatbot.log"

# Cấu hình logging - Tránh duplicate handlers
root_logger = logging.getLogger()
# Xóa tất cả handlers cũ
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Thêm handlers mới
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - (%(name)s) - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ],
    force=True
)

logger = logging.getLogger(__name__)


class ScholarshipChatbot:
    """
    Chatbot tư vấn học bổng - Thread 1 (Refactored với Langchain)
    """
    
    def __init__(self):
        """Khởi tạo Chatbot với Scholarship Agent"""
        logger.info("🔄 Đang khởi tạo chatbot...")
        
        # Validate config
        Config.validate()
        
        # Khởi tạo agent
        self.agent = ScholarshipAgent()
        
        # Conversation memory - lưu lịch sử chat
        self.conversation_history = []
        
        logger.info("✅ Chatbot đã sẵn sàng!\n")
    
    def chat(
        self, 
        query: str, 
        profile_enabled: bool = False,
        user_profile: Optional[Dict[str, Any]] = None,
        timeout: int = 180,
        use_memory: bool = True
    ) -> Dict[str, Any]:
        """
        Xử lý một câu hỏi từ người dùng với timeout protection
        
        Args:
            query: Câu hỏi của người dùng
            profile_enabled: Có sử dụng profile hay không
            user_profile: Dict chứa thông tin profile (nếu có)
            timeout: Thời gian timeout tối đa (giây)
            use_memory: Có sử dụng conversation history hay không
            
        Returns:
            Dict chứa câu trả lời và metadata (bao gồm processing_time_seconds)
        """
        import time
        
        # Bắt đầu đo thời gian
        start_time = time.time()
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Query: {query}")
        logger.info(f"Profile: {'Enabled' if profile_enabled else 'Disabled'}")
        logger.info(f"Memory: {len(self.conversation_history)} previous messages")
        logger.info(f"{'='*80}\n")
        
        # Thêm conversation history vào query nếu có
        enhanced_query = query
        if use_memory and self.conversation_history:
            # Lấy 3 cặp hội thoại gần nhất (6 messages)
            recent_history = self.conversation_history[-6:]
            history_text = "\n".join([
                f"{'User' if i % 2 == 0 else 'Assistant'}: {msg}"
                for i, msg in enumerate(recent_history)
            ])
            enhanced_query = f"[Conversation History]\n{history_text}\n\n[Current Question]\n{query}"
        
        result = {"error": None, "data": None}
        
        def chat_worker():
            try:
                result["data"] = self.agent.run(
                    query=enhanced_query,
                    original_query=query,  # Truyền query gốc để detect language
                    profile_enabled=profile_enabled,
                    user_profile=user_profile
                )
            except Exception as e:
                result["error"] = str(e)
                logger.error(f"Error in chat_worker: {e}", exc_info=True)
        
        # Chạy chat trong thread với timeout
        thread = threading.Thread(target=chat_worker, daemon=True)
        thread.start()
        thread.join(timeout=timeout)
        
        # Kiểm tra timeout
        if thread.is_alive():
            elapsed_time = time.time() - start_time
            logger.warning(f"❌ TIMEOUT: Chat exceeded {timeout}s (actual: {elapsed_time:.2f}s)")
            return {
                "query": query,
                "answer": f"Xin lỗi, câu hỏi của bạn mất quá nhiều thời gian xử lý (>{timeout}s). Vui lòng thử lại với câu hỏi ngắn gọn hơn.",
                "intent": "timeout",
                "confidence": 0.0,
                "tools_used": [],
                "metadata": {
                    "timeout": True, 
                    "timeout_seconds": timeout,
                    "processing_time_seconds": elapsed_time
                }
            }
        
        # Kiểm tra lỗi
        if result.get("error"):
            elapsed_time = time.time() - start_time
            logger.error(f"❌ Error: {result['error']} (after {elapsed_time:.2f}s)")
            return {
                "query": query,
                "answer": f"Xin lỗi, đã xảy ra lỗi: {result['error']}",
                "intent": "error",
                "confidence": 0.0,
                "tools_used": [],
                "metadata": {
                    "error": result["error"],
                    "processing_time_seconds": elapsed_time
                }
            }
        
        # Tính thời gian xử lý
        elapsed_time = time.time() - start_time
        
        # Log kết quả
        final_result = result.get("data", {})
        logger.info(f"\n--- 🤖 Response ---")
        logger.info(f"Intent: {final_result.get('intent')}")
        logger.info(f"Confidence: {final_result.get('confidence', 0):.2f}")
        logger.info(f"Tools: {final_result.get('tools_used', [])}")
        logger.info(f"Processing Time: {elapsed_time:.2f}s")
        logger.info(f"Answer: {final_result.get('answer', '')[:200]}...")
        logger.info(f"{'='*80}\n")
        
        # Thêm processing time vào metadata
        if 'metadata' not in final_result:
            final_result['metadata'] = {}
        final_result['metadata']['processing_time_seconds'] = round(elapsed_time, 2)
        
        # Lưu vào conversation history
        if use_memory and final_result.get('answer'):
            self.conversation_history.append(query)
            self.conversation_history.append(final_result.get('answer', ''))
            # Giới hạn history ở 20 messages (10 cặp hội thoại)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
        
        return final_result
    
    def clear_memory(self):
        """Xóa conversation history"""
        self.conversation_history = []
        logger.info("🗑️ Đã xóa conversation history")

def interactive_mode():
    """Chế độ interactive - nhập query từ console"""
    chatbot = ScholarshipChatbot()
    
    print("\n" + "="*80)
    print("🤖 SCHOLARSHIP CHATBOT - INTERACTIVE MODE")
    print("="*80)
    print("Commands:")
    print("  - Type your question to chat")
    print("  - Type 'profile' to enable profile mode")
    print("  - Type 'clear' to clear conversation history")
    print("  - Type 'exit' or 'quit' to stop")
    print("="*80 + "\n")
    
    profile_enabled = False
    user_profile = None
    
    while True:
        try:
            query = input("You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'profile':
                from services.chatbot_thread1.example_profiles import get_sample_profile
                profile_enabled = not profile_enabled
                if profile_enabled:
                    user_profile = get_sample_profile()
                    print(f"✅ Profile mode: ON")
                else:
                    user_profile = None
                    print(f"❌ Profile mode: OFF")
                continue
            
            # Chat
            result = chatbot.chat(
                query=query,
                profile_enabled=profile_enabled,
                user_profile=user_profile
            )
            
            print(f"\nBot: {result.get('answer', 'No answer')}\n")
            
            # Hiển thị metadata
            processing_time = result.get('metadata', {}).get('processing_time_seconds', 0)
            print(f"[Intent: {result.get('intent')} | Confidence: {result.get('confidence', 0):.2f} | Time: {processing_time:.2f}s]\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    import sys
    
    # Kiểm tra arguments
    if len(sys.argv) > 1:
        # Mode: python main.py "your query here"
        query = " ".join(sys.argv[1:])
        chatbot = ScholarshipChatbot()
        result = chatbot.chat(query)
        print(f"\n{result.get('answer')}")
    else:
        # Mode: Interactive
        interactive_mode()
    
    logging.shutdown()
