# data_collection/prompts/structuring.py

from langchain_core.prompts import PromptTemplate
# Import schema từ file plan_and_analyze (Giữ nguyên)
from .plan_and_analyze import JSON_STRUCTURE_TEMPLATE

# SỬA: Thêm "Eligible_Field_Group"
FLAT_JSON_SCHEMA_ENGLISH = """
{{
  "Scholarship_Name": "",
  "Scholarship_Type": "",  // Comma-separated. Allowed values MUST map to: "Government", "University", "Organization/Foundation".
  "Country": "",           // Must be the name of the study country for the scholarship. If it's an organization/foundation, Country must be the names of all participating countries, comma-separated. 
  "Funding_Level": "",     // Comma-separated categories. Allowed values MUST map to: "Full scholarship", "Tuition Waiver", "Stipend", "Accommodation", "Partial Funding", "Fixed Amount", "Other Costs"
  "Funding_Details": "",   // Keep bullet points/newlines
  "Application_Mode": "",  // ONLY ONE of: "Annual", "Rolling"
  "End_Date": "YYYY-MM-DD",// Format: "YYYY-MM-DD" IF YYYY is 2025, OR "" (Represents the specific Application Deadline Date).
  "Quantity": "",          // e.g., "Globally: 100, Vietnam: 5"
  "Eligibility_Criteria": "", // Merged field for all eligibility info
  
  "Eligible_Fields": "",   // Comma-separated list of SPECIFIC fields
  "Eligible_Field_Group": "", // Comma-separated list of BROAD groups
  
  "Required_Degree": "",   // Comma-separated (select one or more): 
                           // "High School Diploma", "Final Year High School Student", 
                           // "Bachelor's degree", "Bachelor's equivalent", "Final Year Student", 
                           // "Master's degree", "Master's equivalent", "MPhil", "PhD"
  "Min_Gpa": "",           // If multiple cases have different minimum GPAs, list them with context.
  "Bachelor_Field_Relevance": "", //  ONLY ONE of: "Strictly required", "Loosely required", "Not mentioned"
  "Experience_Years": "",  // String. e.g., "2 years full-time"
  "Min_Working_Hours": "", // String. e.g., "2800 hours"
  "Language_Certificate": "",
  "Age": "",               // String. e.g., "Under 35"
  "Gender": "",            // "Male", "Female", "No requirement"
  "Special_Circumstances": "",  
  "Career_Plan": "",
  "Other_Requirements": "", 
  "Scholarship_Info": "",  // A brief, general overview of the scholarship program (be careful not to confuse this with funding level details)
  "Application_Documents": "", // Keep staged structure if possible
  "Timeline": "", // Chronological list. Format MUST be: <Time> : <Event>. e.g., "15 January 2025 : Application Deadline"
  "Url": "" // MUST be the URL of the official scholarship website or application page, if can not find the official URL pick the most relevant one.
}}
"""

# MỚI: Danh sách ngành chuẩn (Giữ nguyên từ prompt của bạn)
STANDARDIZED_FIELDS_AND_GROUPS = """
**📊 BUSINESS & ECONOMICS:**
Agribusiness, Business Administration, Business Analytics, Business Management, Commercial Law, Economics, Finance, Innovation, International Business, International Management, International Trade, Logistics, Marketing, Digital Marketing, Strategic Marketing Management, MBA, Private Sector Development, Taxation, Wealth Management

**💻 STEM - COMPUTER SCIENCE & TECHNOLOGY:**
Advanced Technologies, Artificial Intelligence, Computer Science, Cybersecurity, Data Science, Digital Technologies, Machine Learning, Robotics

**🔧 STEM - ENGINEERING:**
Aeronautical Engineering, Automotive Engineering, Biomedical Engineering, Civil Engineering, Electrical Engineering, Environmental Engineering, Hydro Science and Engineering, Mechanical Engineering, Sustainable Energy Technologies, Renewable Energy

**🔬 STEM - NATURAL SCIENCES:**
Agricultural Sciences, Forest Sciences, Biology, Life Sciences, Biomedicine, Chemistry, Environmental Science, Food Science, Marine Science, Lacustrine Science, Mathematics, Physics

**🏛️ STEM - ARCHITECTURE & PLANNING:**
Architecture, Urban Planning, Transport Engineering

**🌍 SOCIAL SCIENCES & HUMANITIES:**
Anthropology, Development Studies, Food Security, Gender Studies, Gender and Development Studies, Global Affairs, International Affairs, International Relations, Globalization, History, Journalism, Linguistics, Media Studies, Digital Media, Peace Studies, Mediation, Conflict Research, Sociology

**⚖️ LAW, POLITICS & GOVERNANCE:**
Good Governance, Human Rights Law, International Law, Law, Public Policy, Political Science, Public Administration, Security, Rule of Law, Transnational Justice

**❤️ HEALTH & MEDICINE:**
Clinical Medicine, Dentistry, Deglutology, Epidemiology, Global Health, Health Economics, Health Policy, Health Management, Medicine, Pharmacy, Public Health, Sexual Health, Reproductive Health

**🎓 EDUCATION:**
Education Management, Educational Administration, Psychology of Education, TESOL, Learning, Education and Technology

**🎨 ARTS & DESIGN:**
Art History, Design, Product Design, Fashion Design, Film Studies, Music, Theater Arts

**🌱 INTERDISCIPLINARY & SPECIALIZED:**
Climate Change, Climate Change Adaptation, Disaster Risk Management, Environmental Management, Environmental Governance, Sustainable Development
"""

# MỚI: Quy tắc chuẩn hóa (Giữ nguyên từ prompt của bạn)
FIELD_NORMALIZATION_RULES = """
1.  **Exact Matching:** If input mentions a field name (e.g., "Finance"), use it exactly:
    * `Eligible_Fields`: "Finance"
    * `Eligible_Field_Group`: "BUSINESS & ECONOMICS"

2.  **Synonym Mapping:** Map variations to standard names:
    * "CS" / "IT" -> `Eligible_Fields`: "Computer Science", `Eligible_Field_Group`: "STEM - COMPUTER SCIENCE & TECHNOLOGY"
    * "AI" / "ML" -> `Eligible_Fields`: "Artificial Intelligence, Machine Learning", `Eligible_Field_Group`: "STEM - COMPUTER SCIENCE & TECHNOLOGY"
    * "Business" -> `Eligible_Fields`: "Business Administration, Business Management", `Eligible_Field_Group`: "BUSINESS & ECONOMICS"

3.  **Broad Category Expansion:** When input mentions a broad category (e.g., "Engineering"), you MUST:
    * `Eligible_Fields`: Expand to ALL specific fields in that category (e.g., "Aeronautical Engineering, Automotive Engineering, ...").
    * `Eligible_Field_Group`: Add the single group name (e.g., "STEM - ENGINEERING").

4.  **Multiple Categories:** If the input mentions multiple groups (e.g., "STEM and Business"):
    * `Eligible_Fields`: List ALL fields from ALL matched groups, comma-separated.
    * `Eligible_Field_Group`: List ALL matched GROUP NAMES, comma-separated (e.g., "STEM - COMPUTER SCIENCE & TECHNOLOGY, STEM - ENGINEERING, BUSINESS & ECONOMICS").

5.  **Special Cases:**
    * Input: "All fields" / "No restrictions" / "Any Master's program" -> `Eligible_Fields`: "All fields", `Eligible_Field_Group`: "All fields"
    * Input: "" (Empty) -> `Eligible_Fields`: "All fields", `Eligible_Field_Group`: "All fields"

6.  **Output Format:** Both fields must be a single comma-separated string.
"""

# SỬA: Cập nhật prompt chính, nhúng các quy tắc chuẩn hóa vào
STRUCTURING_PROMPT_TEMPLATE = """
**TASK:** You are an expert data structuring agent. Your job is to convert a comprehensive **Text Report** into a single, flat, structured **English** JSON object, following specific data type and formatting rules.

**INPUT TEXT REPORT (Your *only* source of truth):**
{synthesis_report}

---
**INSTRUCTIONS:**

1.  **Map Data:** Read the **Input Text Report** carefully.
2.  **Strict Data Types & Formatting:** Follow the rules exactly as specified in the target schema.
  * **`Min_Gpa` (String):** Include value + scale; if different programs have different minimum GPAs, list with context (e.g., "Master: 3.2/4.0, PhD: 3.5/4.0", or "Range varies: 2.8–3.7 depending on program"); if scale missing, infer common scale; if not specified, use "Not specified".
  * **`Experience_Years` (String):** Extract the requirement as text, **including its context (e.g., "2 years of full-time work", "3 years of relevant experience", "Not required")**. Do NOT convert to a number.
  * **`Min_Working_Hours` (String):** Extract the requirement as text, **including its context (e.g., "2800 hours full-time", "Not specified")**. Do NOT convert to a number.
  * **`Age` (String):** Extract the requirement as text. e.g., "Under 35", "No age limit".
  * **`Dates (End_Date)`:** Must be formatted as **YYYY-MM-DD**. If the input is "15 January 2025", output "2025-01-15". If not available or vague, use `null` or `""`.
  * **`Required_Degree` (Category):** Map the text to the allowed values (e.g., "High School Diploma" for Bachelor's applicants, "Bachelor's degree" for Master's applicants, "Master's degree" for PhD applicants). Use the comma-separated list from the schema comment.
3.  **Accuracy:** Do not add information that is not present in the Text Report.

---
**CRITICAL INSTRUCTION: `Eligible_Fields` & `Eligible_Field_Group` NORMALIZATION**

This is your most important task. When filling the `Eligible_Fields` and `Eligible_Field_Group` keys, you MUST follow these rules.

**STANDARDIZED FIELD NAMES & GROUPS (You MUST use ONLY these exact names):**
""" + STANDARDIZED_FIELDS_AND_GROUPS + """

**NORMALIZATION RULES:**
""" + FIELD_NORMALIZATION_RULES + """
---

**TARGET SCHEMA (English):**
""" + FLAT_JSON_SCHEMA_ENGLISH + """

---
**OUTPUT FORMAT:**
Respond with ONLY the single, structured **English** JSON object.
"""

# input_variables giữ nguyên
structuring_prompt = PromptTemplate(
    input_variables=["synthesis_report"],
    template=STRUCTURING_PROMPT_TEMPLATE
)