# data_collection/prompts/structuring.py

from langchain_core.prompts import PromptTemplate
# Import schema từ file plan_and_analyze (Giữ nguyên)
from .plan_and_analyze import JSON_STRUCTURE_TEMPLATE

# SỬA: Thêm "Eligible_Field_Group"
FLAT_JSON_SCHEMA_ENGLISH = """
{{
  "Scholarship_Name": "",
  "Wanted_Degree": "",     
  "Scholarship_Type": "",  // Comma-separated. Allowed values MUST map to: "Government", "University", "Organization/Foundation".
  "Country": "",           // Must be the name of the study country for the scholarship. If it's an organization/foundation, Country must be the names of all participating countries, comma-separated. 
  "Funding_Level": "",     // Comma-separated categories. Allowed values MUST map to: "Full scholarship", "Tuition Waiver", "Stipend", "Accommodation", "Partial Funding", "Fixed Amount", "Other Costs"
  "Funding_Details": "",   // Keep bullet points/newlines
  "Application_Mode": "",  // ONLY ONE of: "Annual", "Rolling"
  "End_Date": "YYYY-MM-DD",// Format: "YYYY-MM-DD" IF YYYY is 2026, OR "" (Represents the specific Application Deadline Date).
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
  "Timeline": "", // Chronological list. Format MUST be: <Time> : <Event>. e.g., "15 January 2026 : Application Deadline"
  "Url": "" // MUST be the URL of the official scholarship website or application page, if can not find the official URL pick the most relevant one.
}}
"""

# SỬA: Danh sách ngành chuẩn mới với 16 nhóm
STANDARDIZED_FIELDS_AND_GROUPS = """
**1. Education & Training:**
Basic programmes and qualifications, Literacy and numeracy, Personal skills and development, Education science, Training for pre-school teachers, Teacher training without subject specialisation, Teacher training with subject specialisation

**2. Arts, Design & Media:**
Audio-visual techniques and media production, Fashion, interior and industrial design, Fine arts, Handicrafts, Music and performing arts, Visual Arts, Theatre/Drama, Game Design, Game Development, Journalism and reporting, Arts Administration/Management

**3. Humanities & Social Sciences:**
Religion and theology, History and archaeology, Philosophy and ethics, Language acquisition, Literature and linguistics, Inter-disciplinary programmes involving arts and humanities, Political sciences and civics, Psychology, Sociology and cultural studies, International Relations, Area Studies

**4. Economics & Business:**
Economics, Accounting and taxation, Finance, banking and insurance, Management and administration, Marketing and advertising, Secretarial and office work, Wholesale and retail sales, Work skills

**5. Law & Public Policy:**
Law, Political sciences and civics, Public Health, International Development

**6. Natural Sciences:**
Biology, Biochemistry, Environmental sciences, Natural environments and wildlife, Chemistry, Earth sciences, Physics, Astronomy, Mathematics, Statistics

**7. IT & Data Science:**
Computer use, Database and network design and administration, Software and applications development and analysis, Data Science, Data Analytics, Data Engineering, Artificial Intelligence, Cyber Security

**8. Engineering & Technology:**
Nanotechnology, Chemical engineering and processes, Environmental protection technology, Electricity and energy, Electronics and automation, Mechanics and metal trades, Motor vehicles, ships and aircraft, Food processing, Materials (glass, paper, plastic and wood), Textiles (clothes, footwear and leather), Mining and extraction, Sustainable Energy Solutions and Innovation, Renewable Energy Management, Quantum Technologies, Quantum Engineering, Advanced Materials Science, Advanced Materials Engineering

**9. Construction & Planning:**
Architecture and town planning, Building and civil engineering, Urban and Regional Planning

**10. Agriculture & Environment:**
Agricultural/Biosystems Engineering, Crop and livestock production, Agroecology and Sustainable Agriculture, Horticulture, Food Science, Forestry, Fisheries, Veterinary, Animal Science, Environmental sciences, Natural environments and wildlife, Environmental protection technology, Climate Change Adaptation, Climate Change Mitigation

**11. Healthcare & Medicine:**
Dental studies, Medicine, Nursing and midwifery, Medical diagnostic and treatment technology, Therapy and rehabilitation, Pharmacy, Pharmaceutical Science, Traditional and complementary medicine and therapy, Public Health, Global Health Architecture, Clinical Mental Health Counseling, Nutrition Science

**12. Social Services & Care:**
Care of the elderly and of disabled adults, Child care and youth services, Social work and counselling, Clinical Mental Health Counseling, Psychology

**13. Personal Services & Tourism:**
Domestic services, Hair and beauty services, Hotel, restaurants and catering, Sports, Travel, tourism and leisure

**14. Security & Defense:**
Occupational health and safety, Military and defence, Protection of persons and property, Maritime Security, Community sanitation, Cyber Security

**15. Library & Information Management:**
Library, information and archival studies, Information Science, Library Science, Information Science

**16. Transportation & Logistics:**
Transport services, Motor vehicles, ships and aircraft
"""
# SỬA: Cập nhật Quy tắc Chuẩn hóa
# FIELD_NORMALIZATION_RULES = """
# **Your goal is to populate two fields: `Eligible_Field_Group` and `Eligible_Fields`.**

# 1.  **Rule 1: Specific Field Mapping (Highest Priority)**
#     * Read the input. If you see a **specific field** (e.g., "Finance", "CS", "AI", "Civil Engineering"), find its standardized name in the list.
#     * **Action:**
#         * Add the standardized **specific field** (e.g., "Finance", "Computer Science") to the `Eligible_Fields` list.
#         * *Automatically* add its corresponding **group name** (e.g., "Economics & Business") to the `Eligible_Field_Group` list.
#     * *Example:* Input "Studies in Finance and AI."
#         * `Eligible_Fields`: "Finance, Artificial Intelligence"
#         * `Eligible_Field_Group`: "Economics & Business, IT & Data Science"

# 2.  **Rule 2: Broad Group Mapping (Only if specific fields are absent)**
#     * Read the input. If it *only* mentions a **broad group** (e.g., "Engineering", "Arts", "Sciences") and *not* any specific fields within that group...
#     * **Action:**
#         * `Eligible_Fields`: **Leave this field empty** (`""` or `null`).
#         * `Eligible_Field_Group`: Add the standardized **group name(s)** (e.g., "Engineering & Technology", "Arts, Design & Media", "Natural Sciences").
#     * *Example:* Input "We fund students in Engineering, Arts, and IT fields."
#         * `Eligible_Fields`: ""
#         * `Eligible_Field_Group`: "Engineering & Technology, Arts, Design & Media, IT & Data Science"

# 3.  **Rule 3: Synonym Mapping**
#     * Map common variations to their *standardized specific field* and follow Rule 1.
#     * "CS" / "IT" / "Computing" / "Software Engineering" -> Map to "Computer Science".
#     * "AI" / "ML" -> Map to "Artificial Intelligence", "Machine learning".
#     * "Business" / "Management" -> Map to "Business Administration", "Management and administration".
#     * "Public Health" -> Map to "Public Health".
#     * "Humanities" -> Map to "Humanities & Social Sciences" (as a group, Rule 2).

# 4.  **Rule 4: Special Cases (Overrides all)**
#     * Input: "All fields" / "No restrictions" / "Any Master's program" / "All fields of university" / "" (Empty)
#     * **Action:**
#         * `Eligible_Fields`: "All fields"
#         * `Eligible_Field_Group`: "All fields"

# 5.  **Output Format:** Both fields must be a single, comma-separated string. Ensure no duplicate entries in a single list.
# """


# SỬA: Cập nhật prompt chính
STRUCTURING_PROMPT_TEMPLATE = """
**TASK:** You are an expert data structuring agent. Your job is to convert a comprehensive **Text Report** into a single, flat, structured **English** JSON object, following specific data type and formatting rules.

**INPUT TEXT REPORT (Your *only* source of truth):**
{synthesis_report}

---
**INSTRUCTIONS:**

1.  **Map Data:** Read the **Input Text Report** carefully.
2.  **Strict Data Types & Formatting:** Follow the rules exactly.
    * **`Country` (Normalization):** Standardize common country names.
            * "United Kingdom", "England", "Great Britain", "UK" -> "UK"
            * "United States", "America", "USA" -> "USA"
    * **`Min_Gpa` (String):** Include value + scale; if different programs have different minimum GPAs, list with context (e.g., "Master: 3.2/4.0, PhD: 3.5/4.0", or "Range varies: 2.8–3.7 depending on program"); if scale missing, infer common scale; if not specified, use "Not specified".
    * **`Experience_Years` (String):** Extract the requirement as text, **including its context (e.g., "2 years of full-time work", "3 years of relevant experience", "Not required")**. Do NOT convert to a number.
    * **`Min_Working_Hours` (String):** Extract the requirement as text, **including its context (e.g., "2800 hours full-time", "Not specified")**. Do NOT convert to a number.
    * **`Dates (End_Date)`:** Must be **YYYY-MM-DD**. (e.g., "15 January 2026" -> "2026-01-15").
    * **`Required_Degree` (Category):** Map the text to the allowed values (e.g., "High School Diploma" for Bachelor's applicants, "Bachelor's degree" for Master's applicants, "Master's degree" for PhD applicants). Use the comma-separated list from the schema comment.

3.  **Accuracy:** Do not add information that is not present in the Text Report.

---
**CRITICAL INSTRUCTION: `Eligible_Fields` & `Eligible_Field_Group`**

You must populate *both* fields based on these new rules:

**STANDARDIZED GROUP LIST (The official 16 groups):**
""" + STANDARDIZED_FIELDS_AND_GROUPS + """

**NEW RULES:**

1.  **`Eligible_Fields` (Raw Text Field):**
    * Find the part of the Input Text Report describing eligible fields.
    * Copy the text **exactly** as it is written (or summarize it concisely if it is very long).
    * **Example 1:** If report says "Engineering and Arts", this field MUST be "Engineering, Arts".
    * **Example 2:** If report says "Computer Science, Finance", this field MUST be "Computer Science, Finance".
    * **Example 3:** If report says "All fields", this field MUST be "All fields".

2.  **`Eligible_Field_Group` (Standardized Filter Field):**
    * Look at the *raw text* you found in the step above (e.g., "Engineering and Arts", "Computer Science, Finance").
    * Map *each* raw name to its corresponding standardized group from the **STANDARDIZED GROUP LIST**.
    * **Example 1:** Input text "Engineering and Arts".
        * `Eligible_Field_Group`: "Engineering & Technology, Arts, Design & Media"
    * **Example 2:** Input text "Computer Science, Finance".
        * `Eligible_Field_Group`: "IT & Data Science, Economics & Business"
    * **Example 3:** Input text "STEM fields".
        * `Eligible_Field_Group`: "IT & Data Science, Engineering & Technology, Natural Sciences, Construction & Planning" (vì STEM bao gồm 4 nhóm)
    * Combine all unique group names, separated by a comma.

3.  **Special Case:**
    * If the input is "All fields", "No restrictions", "All fields of university", etc.
    * Both fields MUST be "All fields".

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