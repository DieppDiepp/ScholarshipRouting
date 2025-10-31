# data_collection/prompts/structuring.py

from langchain_core.prompts import PromptTemplate

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

STRUCTURING_PROMPT_TEMPLATE = """
**TASK:** You are an expert data structuring agent. Your job is to convert a nested, English JSON report into a single, flat, structured **English** JSON object, following specific data type and formatting rules, with a **critical focus on category standardization** for search system compatibility.

**INPUT REPORT (English, Nested):**
{final_report}

---
**INSTRUCTIONS:**

1.  **Data Mapping Priority:** Read the input report and map its data STRICTLY to the target flat schema provided below.
2.  **STRICT Data Types & Formatting (Crucial for Elasticsearch):**
    * **Boolean/Integer/Float:**
        * **Boolean (For_Vietnamese, Field_Restriction):** Must be literal `true` or `false`.
        * **Integer (Min_Working_Hours):** Must be an integer (e.g., `0`, `40`).
        * **Float (Min_Gpa, Experience_Years):** Must be a number (e.g., `2.0`, `3.3`). Use the numerical default value (e.g., `0.0`) if the requirement is not stated.
    * **Dates:** Format as **DD/MM/YYYY**. Use `""` if vague or missing.
    * **Language_Certificate:** Format **MUST** be `<Certificate Name><space><Score Level>`. E.g., "IELTS 7.0".
    * **Timeline:** Format **MUST** be a chronological list of `<Time> : <Event>`. E.g., "15 January 2025 : Application Deadline".
3.  **CATEGORY FIELDS - STRICT MAPPING (Use ONLY Allowed Values):**
    * For the fields below, you **MUST ONLY** use the allowed values specified. Map descriptive text from the input report to these standardized categories.
        * **Scholarship_Type:** ONLY use: `Government`, `University`, `Organization/Foundation`.
        * **Funding_Level:** Use a comma-separated combination of ONLY: `Full scholarship`, `Tuition Waiver`, `Stipend`, `Accommodation`, `Partial Funding`, `Fixed Amount`, `Other Costs`.
        * **Application_Mode:** ONLY use: `Annual`, `Rolling`.
        * **Bachelor_Field_Relevance:** ONLY use: `Strictly required`, `Loosely required`, `Not mentioned`.
        * **Gender:** ONLY use: `Male`, `Female`, `No requirement`.
        * **Required_Degree:** Use a comma-separated combination of ONLY: `Bachelor's degree`, `Bachelor's equivalent`, `None`, `Master's degree`, `PhD`.
        * **Academic_Certificate:** Use a comma-separated combination of ONLY: `Not required`, `GMAT`, `GRE`, or other relevant degree/certification names.

**TARGET SCHEMA (English):**
""" + FLAT_JSON_SCHEMA_ENGLISH + """

---
**OUTPUT FORMAT:**
Respond with ONLY the single, structured **English** JSON object. Do not include any explanations or markdown backticks.
"""

# Tạo PromptTemplate (chỉ cần final_report làm input)
structuring_prompt = PromptTemplate(
    input_variables=["final_report"],
    template=STRUCTURING_PROMPT_TEMPLATE
)