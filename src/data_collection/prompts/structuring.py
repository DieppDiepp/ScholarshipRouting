# data_collection/prompts/structuring.py

from langchain_core.prompts import PromptTemplate
# Import schema từ file plan_and_analyze
from .plan_and_analyze import JSON_STRUCTURE_TEMPLATE

# Schema tiếng Anh phẳng (FLAT_JSON_SCHEMA_ENGLISH) giữ nguyên
# (Mình rút gọn ở đây cho dễ đọc)
FLAT_JSON_SCHEMA_ENGLISH = """
{{
  "Scholarship_Name": "",
  "Scholarship_Type": "",  // ONLY ONE of: "Government", "University", "Organization/Foundation"
  "Country": "",           // Must be the name of the study country for the scholarship. If it's an organization/foundation, Country must be the names of all participating countries, comma-separated.
  "Funding_Level": "",     // Comma-separated categories. Allowed values MUST map to: "Full scholarship", "Tuition Waiver", "Stipend", "Accommodation", "Partial Funding", "Fixed Amount", "Other Costs"
  "Funding_Details": "",   // Keep bullet points/newlines
  "Application_Mode": "",  // ONLY ONE of: "Annual", "Rolling"
  "End_Date": "",          // "YYYY-MM-DD" IF YYYY is 2025, OR "" (Represents the specific Application Deadline Date).
  "Quantity": "",          // Specify the quantity and the target group/region. e.g., "Globally: 100, Vietnam: 5"
  "Eligible_Applicants": "",  // Use string based on input report, map boolean if possible
  "Eligible_Fields": "",   // Field groups separated by newlines. Majors within a group separated by commas. e.g., "Field Group: Major 1, Major 2..."
  "Required_Degree": "",   // Comma-separated (select one or more): "Bachelor's degree", "Bachelor's equivalent", "Final Year Student", "Relevant Master's degree"
  "Min_Gpa": "",           // "3.2/4.0", "8.0/10", "Not specified"
  "Bachelor_Field_Relevance": "", // ONLY ONE of: "Strictly required", "Loosely required", "Not mentioned"
  "Experience_Years": "", // "2 years full-time", "Not required"
  "Min_Working_Hours": "",  // "2800 hours", "Not specified"
  "Language_Certificate": "", // If requirements differ by program, list as <Program>: <Certificate Score>; otherwise use a single format like "IELTS 7.0".
  "Academic_Certificate": "", // Comma-separated: "Not required", "GMAT", "GRE", or other relevant degree/certification names.
  "Age": "",               // Use specific age or range. e.g., "Under 30", "25-35", or "" if not specified.
  "Gender": "",            // ONLY ONE of: "Male", "Female", "No requirement"
  "Special_Circumstances": "",  
  "Career_Plan": "",
  "Other_Requirements": "", 
  "Scholarship_Info": "",  // A brief, general overview of the scholarship program (be careful not to confuse this with funding level details)
  "Application_Documents": "", // Keep staged structure if possible
  "Timeline": "",          // Chronological list. Format MUST be: <Time> : <Event>. e.g., "15 January 2025 : Application Deadline"
  "Url": ""               // MUST be the URL of the official scholarship website or application page, if can not find the official URL pick the most relevant one.
}}
"""

STRUCTURING_PROMPT_TEMPLATE = """
**TASK:** You are an expert data structuring agent. Your job is to convert a comprehensive **Text Report** into a single, flat, structured **English** JSON object, following specific data type and formatting rules.

**INPUT TEXT REPORT (Your *only* source of truth):**
{synthesis_report}

---
**INSTRUCTIONS:**

1.  **Map Data:** Read the **Input Text Report** carefully.
2.  **Strict Data Types & Formatting:** Follow the rules exactly as specified in the target schema.
* **`Min_Gpa` (String):** Extract the value AND its scale. e.g., "3.2/4.0", "8.5/10". If the scale is not mentioned (e.g., "GPA 3.2"), infer the most common scale (4.0 or 10.0). If not specified, use "Not specified" or `null`.
  * **`Experience_Years` (String):** Extract the requirement as text. e.g., "2 years of full-time work", "Not required". Do NOT convert to a number.
  * **`Min_Working_Hours` (String):** Extract the requirement as text. e.g., "2800 hours", "Not specified". Do NOT convert to a number.
  * **`Age` (String):** Extract the requirement as text. e.g., "Under 35", "No age limit".
  * **`Dates (End_Date)`:** Must be formatted as **YYYY-MM-DD**. If the input is "15 January 2025", output "2025-01-15". If not available or vague, use `null` or `""`.
  * **Category Fields:** Map the text to the allowed values (e.g., "Full scholarship", "Annual").
  * **`Eligibility_Applicants`:** This is the merged field. Summarize all information about applicant eligibility here (citizenship, age, work, etc.).
3.  **Accuracy:** Do not add information that is not present in the Text Report.

**TARGET SCHEMA (English):**
""" + FLAT_JSON_SCHEMA_ENGLISH + """

---
**OUTPUT FORMAT:**
Respond with ONLY the single, structured **English** JSON object.
"""

# input_variables giữ nguyên (chỉ cần 'synthesis_report')
structuring_prompt = PromptTemplate(
    input_variables=["synthesis_report"],
    template=STRUCTURING_PROMPT_TEMPLATE
)