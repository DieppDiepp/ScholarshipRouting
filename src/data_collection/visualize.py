# data_collection/visualize.py

import os
from agent.tools import RotatingTavilyTool
from agent.graph import LangGraphSearchAgent

def generate_graph_image():
    print("🎨 Đang tạo sơ đồ kiến trúc hệ thống...")

    # 1. Khởi tạo Agent với dữ liệu giả (Dummy data)
    # Chúng ta chỉ cần build graph, không chạy, nên key giả là được
    dummy_tavily_keys = ["dummy_key"]
    dummy_google_keys = ["dummy_key"]
    
    tool = RotatingTavilyTool(api_keys=dummy_tavily_keys)
    agent = LangGraphSearchAgent(tool=tool, google_api_keys=dummy_google_keys)

    # 2. Lấy đối tượng Graph
    graph = agent.app.get_graph()

    # 3. Xuất ra file ảnh (PNG)
    try:
        image_data = graph.draw_mermaid_png()
        
        output_file = "agent_architecture.png"
        with open(output_file, "wb") as f:
            f.write(image_data)
            
        print(f"✅ Thành công! Ảnh đã được lưu tại: {os.path.abspath(output_file)}")
        print("Bạn có thể chèn ảnh này vào slide báo cáo.")
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo ảnh: {e}")
        print("Gợi ý: Hãy chắc chắn bạn đã cài đặt thư viện: pip install grandalf")

    # 4. (Tùy chọn) In ra Mermaid Code
    # Bạn có thể copy đoạn code này và dán vào https://mermaid.live để chỉnh sửa đẹp hơn
    print("\n--- MERMAID CODE (Copy vào mermaid.live để chỉnh sửa) ---")
    print(graph.draw_mermaid())
    print("-------------------------------------------------------")

if __name__ == "__main__":
    generate_graph_image()