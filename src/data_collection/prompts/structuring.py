# data_collection/prompts/structuring.py

from langchain_core.prompts import PromptTemplate
from .plan_and_analyze import JSON_STRUCTURE_TEMPLATE # Import schema từ file cũ

# SỬA: Schema này giờ là schema đích (tiếng Anh)
# Mình đã xóa trường "Danh_Sách_Nhóm_Ngành" tiếng Việt
FLAT_JSON_SCHEMA_ENGLISH = """
{{
  "Scholarship_Name": "",
  "Scholarship_Type": "",  // ONLY ONE of: "Government", "University", "Organization/Foundation"
  "Country": "",           // Must be the name of the study country for the scholarship. If it's an organization/foundation, Country must be the names of all participating countries, comma-separated.
  "Funding_Level": "",     // Comma-separated categories. Allowed values MUST map to: "Full scholarship", "Tuition Waiver", "Stipend", "Accommodation", "Partial Funding", "Fixed Amount", "Other Costs"
  "Funding_Details": "",   // Keep bullet points/newlines
  "Application_Mode": "",  // ONLY ONE of: "Annual", "Rolling"
  "Application_Month": "", // ONLY ONE of: "1"-"12" IF Application_Mode is "Annual" (Represents the annual application opening month). Use "" if Application_Mode is "Rolling".
  "Start_Date": "",        // "DD/MM/YYYY" IF YYYY is 2025, OR "" (Represents the specific Application Opening Date).
  "End_Date": "",          // "DD/MM/YYYY" IF YYYY is 2025, OR "" (Represents the specific Application Deadline Date).
  "Quantity": "",          // Specify the quantity and the target group/region. e.g., "Globally: 100, Vietnam: 5"
  "For_Vietnamese": false, // ONLY ONE of: true/false
  "Eligibility": "",       // Use string based on input report, map boolean if possible
  "Eligible_Applicants": "", // Keep bullet points/newlines
  "Field_Restriction": false, // ONLY ONE of: true/false
  "Eligible_Fields": "",   // Field groups separated by newlines. Majors within a group separated by commas. e.g., "Field Group: Major 1, Major 2..."
  "Required_Degree": "",   // Comma-separated (select one or more): "Bachelor's degree", "Bachelor's equivalent", "Final Year Student", "Relevant Master's degree"
  "Min_Gpa": 0.0,          // Float (0.0 if not specified)
  "Bachelor_Field_Relevance": "", // ONLY ONE of: "Strictly required", "Loosely required", "Not mentioned"
  "Experience_Years": 0.0, // Float (0.0 if not specified/required)
  "Min_Working_Hours": 0,  // Integer (0 if not specified/required)
  "Language_Certificate": "", // Format MUST be: <Certificate Name><space><Score Level>. e.g., "IELTS 7.0"
  "Academic_Certificate": "", // Comma-separated: "Not required", "GMAT", "GRE", or other relevant degree/certification names.
  "Awards_Requirement": "",   // Keep bullet points/newlines
  "Publication_Requirement": "",  // Keep bullet points/newlines
  "Age": "",               // Use specific age or range. e.g., "Under 30", "25-35", or "" if not specified.
  "Gender": "",            // ONLY ONE of: "Male", "Female", "No requirement"
  "Special_Circumstances": "",  
  "Career_Plan": "",
  "Other_Requirements": "", 
  "Scholarship_Info": "",  // A brief, general overview of the scholarship program (be careful not to confuse this with funding level details)
  "Application_Documents": "", // Keep staged structure if possible
  "Timeline": "",          // Chronological list. Format MUST be: <Time> : <Event>. e.g., "15 January 2025 : Application Deadline"
  "Url": ""               // MUST be the URL of the official scholarship website or application page.
}}
"""

# SỬA: Cập nhật hoàn toàn prompt
STRUCTURING_PROMPT_TEMPLATE = """
**TASK:** You are an expert data extraction agent. Your job is to convert a comprehensive **Text Report** into a single, flat, structured **English** JSON object. You will also receive the **Raw Evidence** for cross-referencing.

**INPUT 1: COMPREHENSIVE TEXT REPORT (Primary Source):**
{synthesis_report}

---
**INPUT 2: ALL RAW WEB EVIDENCE (Secondary Source for details):**
{context}
---

**INSTRUCTIONS:**

1.  **Map Data:** Read **Input 1 (Text Report)** first. This is your primary source.
2.  **Cross-Reference:** Use **Input 2 (Raw Evidence)** to find specific details (like exact GPAs, dates, or list items) that might be summarized in the Text Report.
3.  **Strict Data Types & Formatting:** Follow the rules exactly as specified in the target schema.
    * **boolean:** `true` or `false`.
    * **float:** `2.0`, `3.3`. Use `0.0` if not specified.
    * **string:** Extract English text. Use `""` or `null` for missing values.
    * **Dates:** Format as DD/MM/YYYY. Use `""` or `null` if not specific.
    * **Category Fields:** Map to allowed values (e.g., "Full scholarship", "Annual").
4.  **Accuracy:** You now have ALL information. Be extremely accurate.

**TARGET SCHEMA (English):**
""" + FLAT_JSON_SCHEMA_ENGLISH + """

---
**OUTPUT FORMAT:**
Respond with ONLY the single, structured **English** JSON object.
"""

# SỬA: Cập nhật input_variables
structuring_prompt = PromptTemplate(
    input_variables=["synthesis_report", "context"],
    template=STRUCTURING_PROMPT_TEMPLATE
)