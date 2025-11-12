"""
Run Batch Test - Chạy test hàng loạt từ CSV với giới hạn 3 samples đầu
Có lựa chọn chạy 1 lần 7 file hoặc chạy từng file
"""
import os
import sys
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Thêm thư mục gốc vào sys.path để import được main
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from main import ScholarshipChatbot

class BatchTestRunner:
    """
    Class để chạy batch test từ các file CSV (chỉ 3 samples đầu mỗi file)
    """
    
    def __init__(self, test_case_dir: str = None, output_dir: str = None):
        """
        Khởi tạo Batch Test Runner
        
        Args:
            test_case_dir: Thư mục chứa các file CSV test case (None = tự động tìm)
            output_dir: Thư mục để lưu kết quả test (None = tự động tạo)
        """
        # Tự động xác định đường dẫn nếu không được cung cấp
        if test_case_dir is None:
            current_dir = Path(__file__).parent
            test_case_dir = current_dir / "test_case"
        
        if output_dir is None:
            current_dir = Path(__file__).parent
            output_dir = current_dir / "test_results"
        
        self.test_case_dir = Path(test_case_dir)
        self.output_dir = Path(output_dir)
        self.chatbot = None
        self.max_samples = 1  # Chỉ chạy 3 samples đầu mỗi file
        
        # Tạo thư mục output nếu chưa có
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print("🔧 Đang khởi tạo Batch Test Runner...")
        print(f"⚙️  Cấu hình: Chỉ chạy {self.max_samples} samples đầu mỗi file")
    
    def initialize_chatbot(self):
        """Khởi tạo chatbot """
        if self.chatbot is None:
            self.chatbot = ScholarshipChatbot()
    
    def read_test_cases(self, csv_file: Path, limit: int = None) -> List[Dict[str, Any]]:
        """
        Đọc test cases từ file CSV
        
        Args:
            csv_file: Đường dẫn đến file CSV
            limit: Số lượng test case tối đa (None = tất cả)
            
        Returns:
            List các test case dạng dict
        """
        test_cases = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader):
                    if limit and idx >= limit:
                        break
                    test_cases.append(row)
            
            print(f"✅ Đọc được {len(test_cases)} test cases từ {csv_file.name}")
            return test_cases
            
        except Exception as e:
            print(f"❌ Lỗi khi đọc file {csv_file.name}: {e}")
            return []
    
    def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chạy một test case
        
        Args:
            test_case: Dict chứa thông tin test case
            
        Returns:
            Dict chứa kết quả test
        """
        query = test_case.get('Query (Câu hỏi)', '')
        profile_required = test_case.get('Profile required', '❌ Không')
        
        # Xác định có cần profile không
        profile_enabled = '✅' in profile_required or 'BẮT BUỘC' in profile_required
        
        # Profile mẫu (dùng cho các test case cần profile)
        user_profile = {
            "age": 22,
            "gpa": 3.5,
            "current_degree": "Bachelor",
            "field_of_study": "Computer Science",
            "target_degree": "Master",
            "target_field": "Engineering",
            "language_certificates": [{"type": "IELTS", "score": 7.0}],
            "preferred_countries": ["Turkey", "Hungary", "Thailand"],
            "budget": "Full scholarship"
        }
        
        try:
            # Gọi chatbot
            start_time = time.time()
            result = self.chatbot.chat(
                query=query,
                profile_enabled=profile_enabled,
                user_profile=user_profile if profile_enabled else None
            )
            elapsed_time = time.time() - start_time
            
            return {
                'success': True,
                'answer': result['answer'],
                'intent': result['intent'],
                'confidence': result['confidence'],
                'tools_used': ', '.join(result['tools_used']),
                'elapsed_time': round(elapsed_time, 2),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'answer': f"ERROR: {str(e)}",
                'intent': 'N/A',
                'confidence': 0,
                'tools_used': 'N/A',
                'elapsed_time': 0,
                'error': str(e)
            }
    
    def run_test_file(self, csv_file: Path) -> str:
        """
        Chạy test cases trong một file CSV (chỉ 3 samples đầu)
        
        Args:
            csv_file: Đường dẫn đến file CSV
            
        Returns:
            Đường dẫn đến file kết quả
        """
        print(f"\n{'='*80}")
        print(f"📋 Đang chạy test file: {csv_file.name}")
        print(f"{'='*80}\n")
        
        # Đọc test cases (chỉ lấy 3 đầu)
        test_cases = self.read_test_cases(csv_file, limit=self.max_samples)
        if not test_cases:
            print(f"⚠ Không có test case nào để chạy trong {csv_file.name}")
            return None
        
        # Khởi tạo chatbot (nếu chưa)
        self.initialize_chatbot()
        
        # Chạy từng test case
        results = []
        total = len(test_cases)
        
        for idx, test_case in enumerate(test_cases, 1):
            stt = test_case.get('STT', idx)
            query = test_case.get('Query (Câu hỏi)', '')
            
            print(f"[{idx}/{total}] Test #{stt}: {query[:60]}...")
            
            # Chạy test
            result = self.run_single_test(test_case)
            
            # Lưu kết quả
            results.append({
                'STT': stt,
                'Nhóm Test Case': test_case.get('Nhóm Test Case', ''),
                'Query (Câu hỏi)': query,
                'Profile required': test_case.get('Profile required', ''),
                'Expected (Kết quả mong đợi)': test_case.get('Expected (Kết quả mong đợi)', ''),
                'Answer (Câu trả lời)': result['answer'],
                'Intent': result['intent'],
                'Confidence': result['confidence'],
                'Tools Used': result['tools_used'],
                'Time (s)': result['elapsed_time'],
                'Status': '✅ Success' if result['success'] else '❌ Error',
                'Error': result['error'] or ''
            })
            
            # Hiển thị kết quả ngắn gọn
            status_icon = '✅' if result['success'] else '❌'
            print(f"   {status_icon} Intent: {result['intent']}, Time: {result['elapsed_time']}s")
            
            # Delay nhỏ giữa các request (tránh rate limit)
            time.sleep(0.5)
        
        # Lưu kết quả ra file CSV
        output_file = self._save_results(csv_file.stem, results)
        
        print(f"\n✅ Hoàn thành! Kết quả đã lưu tại: {output_file}")
        print(f"   - Tổng số test: {total}")
        print(f"   - Thành công: {sum(1 for r in results if r['Status'] == '✅ Success')}")
        print(f"   - Lỗi: {sum(1 for r in results if r['Status'] == '❌ Error')}")
        
        return output_file
    
    def _save_results(self, test_name: str, results: List[Dict[str, Any]]) -> str:
        """
        Lưu kết quả test ra file CSV
        
        Args:
            test_name: Tên test case
            results: List kết quả test
            
        Returns:
            Đường dẫn đến file kết quả
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"{test_name}_results_{timestamp}.csv"
        
        # Ghi file CSV
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        return str(output_file)
    
    def run_all_tests(self):
        """
        Chạy tất cả các file test trong thư mục test case (3 samples đầu mỗi file)
        """
        print("\n" + "="*80)
        print("🚀 BẮT ĐẦU BATCH TEST - CHẠY 3 SAMPLES ĐẦU MỖI FILE")
        print("="*80)
        
        # Tìm tất cả file CSV trong thư mục test case
        csv_files = sorted(self.test_case_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"⚠ Không tìm thấy file CSV nào trong {self.test_case_dir}")
            return
        
        print(f"\n📁 Tìm thấy {len(csv_files)} file test:")
        for i, f in enumerate(csv_files, 1):
            print(f"   {i}. {f.name}")
        
        # Khởi tạo chatbot một lần duy nhất
        self.initialize_chatbot()
        
        # Chạy từng file test
        all_output_files = []
        start_time = time.time()
        
        for csv_file in csv_files:
            output_file = self.run_test_file(csv_file)
            if output_file:
                all_output_files.append(output_file)
        
        total_time = time.time() - start_time
        
        # Tổng kết
        print("\n" + "="*80)
        print("🎉 HOÀN THÀNH TẤT CẢ BATCH TEST")
        print("="*80)
        print(f"⏱ Tổng thời gian: {total_time:.2f}s")
        print(f"📊 Số file test: {len(csv_files)}")
        print(f"📊 Tổng số test đã chạy: {len(csv_files) * self.max_samples}")
        print(f"📁 Kết quả đã lưu tại: {self.output_dir}/")
        print("\nCác file kết quả:")
        for i, f in enumerate(all_output_files, 1):
            print(f"   {i}. {Path(f).name}")
        print("="*80 + "\n")
    
    def show_menu(self):
        """
        Hiển thị menu lựa chọn
        """
        print("\n" + "="*80)
        print("📋 BATCH TEST RUNNER - MENU")
        print("="*80)
        print("\n1. Chạy tất cả 7 file test (3 samples đầu mỗi file)")
        print("2. Chạy từng file test riêng lẻ")
        print("3. Thoát")
        print("\n" + "="*80)
        
        choice = input("\nNhập lựa chọn của bạn (1-3): ").strip()
        return choice
    
    def run_individual_tests(self):
        """
        Chạy từng file test riêng lẻ
        """
        # Tìm tất cả file CSV
        csv_files = sorted(self.test_case_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"⚠ Không tìm thấy file CSV nào trong {self.test_case_dir}")
            return
        
        while True:
            print("\n" + "="*80)
            print("📁 CHỌN FILE TEST")
            print("="*80)
            print(f"\nCó {len(csv_files)} file test:")
            for i, f in enumerate(csv_files, 1):
                print(f"   {i}. {f.name}")
            print(f"   {len(csv_files) + 1}. Quay lại menu chính")
            print("\n" + "="*80)
            
            choice = input(f"\nNhập số thứ tự file (1-{len(csv_files) + 1}): ").strip()
            
            try:
                choice_num = int(choice)
                if choice_num == len(csv_files) + 1:
                    break
                elif 1 <= choice_num <= len(csv_files):
                    selected_file = csv_files[choice_num - 1]
                    
                    # Khởi tạo chatbot (nếu chưa)
                    self.initialize_chatbot()
                    
                    # Chạy file test
                    self.run_test_file(selected_file)
                    
                    input("\n[Nhấn Enter để tiếp tục...]")
                else:
                    print("❌ Lựa chọn không hợp lệ!")
            except ValueError:
                print("❌ Vui lòng nhập số!")

def main():
    """
    Hàm main - Menu lựa chọn
    """
    # Khởi tạo runner (sẽ tự động tìm đường dẫn)
    runner = BatchTestRunner()
    
    print("\n" + "#"*80)
    print("SCHOLARSHIP CHATBOT - BATCH TEST RUNNER")
    print("#"*80)
    print(f"\n📁 Test case directory: {runner.test_case_dir}")
    print(f"📁 Output directory: {runner.output_dir}")
    print(f"⚙️  Cấu hình: Chỉ chạy {runner.max_samples} samples đầu mỗi file")
    
    while True:
        choice = runner.show_menu()
        
        if choice == '1':
            # Chạy tất cả file
            runner.run_all_tests()
            input("\n[Nhấn Enter để quay lại menu...]")
        
        elif choice == '2':
            # Chạy từng file
            runner.run_individual_tests()
        
        elif choice == '3':
            print("\n👋 Tạm biệt!")
            break
        
        else:
            print("\n❌ Lựa chọn không hợp lệ! Vui lòng chọn 1-3.")

if __name__ == "__main__":
    main()
