#   * `plan_and_analyze.py`: Prompt phức tạp nhất. Nó yêu cầu LLM: "Dựa trên nội dung web thô sau... hãy điền vào cấu trúc JSON 10 mục này... Sau đó, xác định những mục nào còn thiếu (`null`) và tạo ra một danh sách các câu hỏi tìm kiếm mới để đi tìm chính xác thông tin đó."

# data_collection/prompts/plan_and_analyze.py

from langchain_core.prompts import PromptTemplate

# JSON_STRUCTURE_TEMPLATE (giữ nguyên, đã escape)
JSON_STRUCTURE_TEMPLATE = """
{{
    "basic_info": {{
        "official_name": "...",
        "provider": "...",
        "study_country": "..."
    }},
    "funding_info": {{
        "funding_details": "...",
        "covered_expenses": ["..."]
    }},
    "timeline_info": {{
        "application_deadline": "...",
        "opening_date": "...",
        "number_of_awards": "..."
    }},
    "eligibility_criteria": {{
        "for_vietnamese": "...",
        "age_requirements": "...",
        "work_requirements": "..."
    }},
    "field_restrictions": {{
        "eligible_fields": "...",
        "restrictions": "..."
    }},
    "academic_requirements": {{
        "min_gpa": "...",
        "required_degree": "..."
    }},
    "experience_requirements": {{
        "min_years": "...",
        "accepted_types": "..."
    }},
    "test_requirements": {{
        "ielts_toefl": "...",
        "gmat_gre": "..."
    }},
    "additional_requirements": {{
        "reference_letters": "...",
        "career_plan": "..."
    }},
    "background_and_logistics": {{
        "official_website": "...",
        "application_documents": "...",
        "selection_process": "..."
    }}
}}
"""

# --- ENGLISH PROMPT ---

_ANALYZE_PROMPT_PART_1 = """
**TASK:** You are an expert Scholarship Analyst. You have just received raw web content scraped for the scholarship: "{scholarship_name}".

**RAW SCRAPED WEB CONTENT:**
{context}

---
**YOUR REQUIREMENTS:**

1.  **Analyze & Fill Information:** Carefully read the raw web content above. Fill in as much information as possible into the following JSON structure.
    * Use **ONLY** the information present in the provided content.
    * If information for a specific field cannot be found, leave its value as `null`.

**JSON Structure to Fill:**
"""

_ANALYZE_PROMPT_PART_2 = """

2.  **Identify Missing Information:** Based on the `null` fields in the JSON you just created, generate a list of specific search queries to find that missing information.

3.  **CRITICAL REQUIREMENT: AVOID REPETITION:**
    * Here is a list of queries that were already executed but **failed** to yield new, useful information:
        `{failed_queries}`
    * When creating new `missing_queries`, **DO NOT** repeat any query from this failed list.
    * If you still need information for that topic, **rephrase the query** (e.g., instead of "IELTS requirements", try "English language proficiency test scores").

**OUTPUT FORMAT:**
Respond with a single, raw JSON object only. Do not include any explanations or markdown backticks (```json ... ```). The JSON object must have two keys:
1.  `report_data`: The JSON object (following the structure above) filled with information.
2.  `missing_queries`: A list of new search query strings. If all information is found, return an empty list `[]`.

**Example Output Structure:**
{{
    "report_data": {{
        "basic_info": {{
            "official_name": "Chevening Scholarship",
            "provider": "UK Government",
            "study_country": "UK"
        }},
        "funding_info": {{ ... }},
        "timeline_info": {{
            "application_deadline": null,
            ...
        }},
        ...
    }},
    "missing_queries": [
        "Chevening scholarship application deadline 2025-2026",
        "Chevening scholarship work experience requirements"
    ]
}}

---
**BEGIN TASK FOR SCHOLARSHIP: {scholarship_name}**
"""

# Nối chuỗi lại
ANALYZE_PROMPT_TEMPLATE = (
    _ANALYZE_PROMPT_PART_1
    + JSON_STRUCTURE_TEMPLATE
    + _ANALYZE_PROMPT_PART_2
)

# Thêm "failed_queries" vào danh sách input_variables
analyze_prompt = PromptTemplate(
    input_variables=["scholarship_name", "context", "failed_queries"],
    template=ANALYZE_PROMPT_TEMPLATE
)