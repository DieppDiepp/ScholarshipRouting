# services/user_svc.py
from typing import Any, Dict, List, Optional
from elasticsearch import Elasticsearch
from dtos.user_dtos import UserProfile
from dtos.search_dtos import FilterItem
from services.es_svc import filter_advanced

def map_profile_to_filters(user_profile: UserProfile) -> List[FilterItem]:
    """
    Chuyển đổi UserProfile thành danh sách các FilterItem dựa trên quy tắc.
    Đây là bước "Rule-based Mapping".
    """
    filters: List[FilterItem] = []

    # === Các tiêu chí LỌC CỨNG (inter_field_operator = AND) ===
    # Thường là các trường "desired" mà người dùng đã chọn rõ ràng

    if user_profile.desired_countries:
        filters.append(FilterItem(field="Country", values=user_profile.desired_countries, operator="OR"))
    
    if user_profile.desired_scholarship_type:
        filters.append(FilterItem(field="Scholarship_Type", values=user_profile.desired_scholarship_type, operator="OR"))

    if user_profile.desired_funding_level:
        filters.append(FilterItem(field="Funding_Level", values=user_profile.desired_funding_level, operator="OR"))

    if user_profile.desired_application_mode:
        filters.append(FilterItem(field="Application_Mode", values=user_profile.desired_application_mode, operator="OR"))

    if user_profile.desired_field_of_study:
        # Có thể dùng field_of_study từ CV nếu desired_field_of_study trống
        combined_fields = set(user_profile.desired_field_of_study)
        if user_profile.field_of_study and user_profile.field_of_study not in combined_fields:
            combined_fields.add(user_profile.field_of_study)
        if combined_fields:
            filters.append(FilterItem(field="Eligible_Fields", values=list(combined_fields), operator="OR"))
    elif user_profile.field_of_study: # Chỉ dùng field_of_study từ CV nếu không có desired_field_of_study
        filters.append(FilterItem(field="Eligible_Fields", values=[user_profile.field_of_study], operator="OR"))
    
    # === Các tiêu chí có thể là "mềm" hoặc thêm vào sau ===
    # Ví dụ, nếu bạn có trường Years_of_Experience trong học bổng
    # if user_profile.years_of_experience is not None and user_profile.years_of_experience > 0:
    #     filters.append(FilterItem(field="Min_Experience", values=[str(user_profile.years_of_experience)], operator="AND"))
    # (Đây chỉ là ví dụ, cần mapping cẩn thận với trường trong ES)

    return filters

# services/user_svc.py

# ... (các import và hàm map_profile_to_filters giữ nguyên) ...

def find_matching_scholarships_for_profile(
    client: Elasticsearch,
    user_profile: UserProfile,
    index: str,
    collection: str,
    size: int = 10,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Tìm kiếm học bổng phù hợp dựa trên profile người dùng,
    sử dụng logic "OR" để truy xuất một danh sách rộng các ứng viên tiềm năng
    cho giai đoạn AI Re-ranking sau này.
    """
    filters = map_profile_to_filters(user_profile)

    if not filters:
        # Nếu không có tiêu chí nào từ profile, trả về rỗng hoặc một thông báo
        return {"total": 0, "items": []}
    
    filters_dict = [f.model_dump() for f in filters]

    # --- Luôn sử dụng logic "OR" để đảm bảo một danh sách kết quả đa dạng ---
    # Điều này tạo tiền đề tốt cho AI Re-ranking sau này.
    results = filter_advanced(
        client=client,
        index=index,
        collection=collection,
        filters=filters_dict,
        inter_field_operator="OR",
        size=size,
        offset=offset,
    )

    # Trong tương lai, đây sẽ là nơi bạn đưa 'results["items"]' vào AI Re-ranking
    # For now, we return the ES results directly
    return results