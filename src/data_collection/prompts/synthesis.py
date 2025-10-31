#   * `synthesis.py`: Prompt cuối cùng: "Dựa trên toàn bộ thông tin đã thu thập, hãy tạo báo cáo JSON cuối cùng theo 10 mục. Hãy đảm bảo thông tin là chính xác và được trích xuất từ các nguồn đã cung cấp."

# data_collection/prompts/synthesis.py

from langchain_core.prompts import PromptTemplate

# Lấy lại cấu trúc JSON đã escape từ file kia
# XÓA: Không cần JSON_STRUCTURE_TEMPLATE ở đây nữa
# from .plan_and_analyze import JSON_STRUCTURE_TEMPLATE

SYNTHESIS_PROMPT_TEMPLATE = """
**TASK:** You are a senior research analyst. Your goal is to write a final, comprehensive, and well-structured analytical report (in text/markdown format) on the "{scholarship_name}" scholarship.

You will be given two inputs:
1.  **Draft Report:** A JSON object with the data found so far (may contain nulls).
2.  **All Collected Evidence:** A large block of raw text from all web pages visited.

**INPUT 1: DRAFT REPORT (JSON):**
{draft_report}

---
**INPUT 2: ALL COLLECTED EVIDENCE (Raw Context):**
{context}
---

**YOUR REQUIREMENTS:**

1.  **Write a Comprehensive Report:** Using *both* inputs, write a detailed analytical report in English.
2.  **Structure:** Organize the report logically using Markdown headings (e.g., "## Basic Information", "## Funding and Benefits", "## Eligibility Criteria").
3.  **Synthesize, Don't Just List:** Do not just copy/paste. Synthesize the information from all 20+ documents into a coherent narrative.
4.  **Use All Information:** Use the **Draft Report** as a guide for the structure, but use the **All Collected Evidence** to find details, fill in the gaps (the `null` values), and provide rich context.
5.  **Be Factual:** Stick strictly to the information provided in the inputs.

**OUTPUT FORMAT:**
Respond with ONLY the final, comprehensive text/markdown report. Do not include any other text or explanations.
"""

# Tạo PromptTemplate
synthesis_prompt = PromptTemplate(
    input_variables=["scholarship_name", "context", "draft_report"],
    template=SYNTHESIS_PROMPT_TEMPLATE
)