#   * `synthesis.py`: Prompt cuối cùng: "Dựa trên toàn bộ thông tin đã thu thập, hãy tạo báo cáo JSON cuối cùng theo 10 mục. Hãy đảm bảo thông tin là chính xác và được trích xuất từ các nguồn đã cung cấp."

# data_collection/prompts/synthesis.py

from langchain_core.prompts import PromptTemplate

# Lấy lại cấu trúc JSON đã escape từ file kia
from .plan_and_analyze import JSON_STRUCTURE_TEMPLATE

SYNTHESIS_PROMPT_TEMPLATE = """
**TASK:** You are a final Editor. You have been given a **Draft Report** and all the **Raw Evidence** (scraped web content) that has been collected.

**Scholarship:** {scholarship_name}

**DRAFT REPORT (May contain nulls):**
{draft_report}

---
**ALL COLLECTED EVIDENCE (Raw Context):**
{context}
---

**YOUR REQUIREMENTS:**

1.  **Final Review:** Read the Draft Report.
2.  **Fill Gaps:** Using the All Collected Evidence, perform a final review to see if any information from the Evidence can fill in the remaining `null` fields in the Draft Report.
3.  **No Hallucination:** Only use information from the Evidence. If a field is still `null` after your review, keep it as `null`.
4.  **Final Output:** Return a single, clean JSON object matching the 10-section structure below. Do not add any explanations or markdown backticks.

**Final JSON Structure:**
""" + JSON_STRUCTURE_TEMPLATE # Nối chuỗi

# Tạo PromptTemplate
synthesis_prompt = PromptTemplate(
    input_variables=["scholarship_name", "context", "draft_report"],
    template=SYNTHESIS_PROMPT_TEMPLATE
)