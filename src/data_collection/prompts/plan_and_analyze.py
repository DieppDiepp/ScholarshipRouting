# data_collection/prompts/plan_and_analyze.py

from langchain_core.prompts import PromptTemplate

# SỬA: Xóa các trường không cần thiết khỏi cấu trúc nháp (draft structure)
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
        "eligibility_details": "..." 
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
        "ielts_toefl_other_language_certificates": "..."
    }},
    "additional_requirements": {{
        "reference_letters": "...",
        "career_plan": "...",
        "age_limits": "...", 
        "gender_requirement": "...",
        "special_circumstances": "...",
        "other_requirements": "..."
    }},
    "background_and_logistics": {{
        "official_website": "...",
        "application_documents": "...",
        "selection_process": "...",
        "scholarship_info": "...",
        "timeline_summary": "..."
    }}
}}
"""

# --- ENGLISH PROMPT (Giữ nguyên, chỉ thay đổi input variables) ---

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
    * If you still need information for that topic, **rephrase the query**.

**OUTPUT FORMAT:**
Respond with a single, raw JSON object only. Do not include any explanations or markdown backticks (```json ... ```). The JSON object must have two keys:
1.  `report_data`: The JSON object (following the structure above) filled with information.
2.  `missing_queries`: A list of new search query strings. If all information is found, return an empty list `[]`.

**Example Output Structure:**
{{
    "report_data": {{
        "basic_info": {{
            "official_name": "Chevening Scholarship",
            ...
        }},
        "timeline_info": {{
            "application_deadline": null,
            ...
        }},
        ...
    }},
    "missing_queries": [
        "Chevening scholarship application deadline 2026-2027",
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

# input_variables giữ nguyên (vì các biến {scholarship_name}, {context}, {failed_queries} vẫn được dùng)
analyze_prompt = PromptTemplate(
    input_variables=["scholarship_name", "context", "failed_queries"],
    template=ANALYZE_PROMPT_TEMPLATE
)