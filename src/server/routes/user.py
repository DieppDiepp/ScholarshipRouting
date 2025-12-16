# routes/user.py
import os
from typing import Dict, Any, List
from fastapi import APIRouter, Query, Body, HTTPException, status, Depends
from elasticsearch import Elasticsearch

from services.user_svc import find_matching_scholarships_for_profile
from dtos.user_dtos import (
    UserProfile,
    ScholarshipInterest,
    ScholarshipInterestUpdate,
    ScholarshipApplication,
    ScholarshipApplicationUpdate,
)
from services.auth_svc import (
    get_profile, 
    update_profile,
    verify_firebase_user,
    require_user_ownership,
    AuthenticatedUser
)

router = APIRouter()

ES_HOST = os.getenv("ELASTICSEARCH_HOST")
ES_USER = os.getenv("ELASTIC_USER")
ES_PASS = os.getenv("ELASTIC_PASSWORD")

profile_example_data = {
    "uid": "user123",
    "email": "user@example.com",
    "display_name": "Nguyen Van A",
    "desired_countries": ["Hà Lan", "Mỹ"],
    "desired_funding_level": ["Toàn phần"],
    "desired_field_of_study": ["Kinh tế", "Quản trị kinh doanh"],
    "field_of_study": "Khoa học Máy tính",
    "gpa_range_4": 3.8,
    "years_of_experience": 2.5,
    "notes": "Quan tâm đến các học bổng có chương trình MBA hoặc tài chính.",
    "tags": ["STEM", "MBA"]
}

@router.post(
    "/match-scholarships-by-profile",
    response_model=Dict[str, Any],
    summary="Tìm học bổng phù hợp với hồ sơ người dùng",
    description="Nhận một profile người dùng và trả về danh sách các học bổng tiềm năng được tìm thấy dựa trên các tiêu chí mong muốn. Đây là bước truy xuất ban đầu, chuẩn bị cho giai đoạn AI tái xếp hạng.",
)
def match_scholarships_by_profile(
    # --- Thay đổi ở đây: Bỏ giá trị mặc định, dùng `...` để làm bắt buộc ---
    collection: str = Query(
        ..., # Tham số này giờ là bắt buộc
        description="Tên collection (index) chứa học bổng cần tìm kiếm",
        example="scholarships" # Example vẫn có thể giữ để minh họa
    ),
    size: int = Query(
        10, ge=1, le=100, description="Số lượng kết quả học bổng trả về"
    ),
    offset: int = Query(
        0, ge=0, description="Vị trí bắt đầu lấy kết quả (dùng cho phân trang)"
    ),
    user_profile: UserProfile = Body(
        ...,
        example=profile_example_data,
        description="Toàn bộ thông tin profile của người dùng để tìm học bổng phù hợp."
    )
):
    """
    Endpoint này cho phép người dùng gửi thông tin profile của mình để nhận danh sách các học bổng
    tiềm năng. Hệ thống sẽ sử dụng các quy tắc để chuyển đổi profile thành các bộ lọc tìm kiếm
    trên Elasticsearch.

    Kết quả trả về là một danh sách các học bổng được sắp xếp dựa trên độ phù hợp ban đầu của Elasticsearch.
    Trong các phiên bản sau, kết quả này sẽ được AI phân tích và tái xếp hạng để mang lại độ chính xác cao hơn.
    """
    es = Elasticsearch(
            hosts=[ES_HOST],
            basic_auth=(ES_USER, ES_PASS),
            verify_certs=False,
            max_retries=30,
            retry_on_timeout=True,
            request_timeout=30,
        )
    try:

        return find_matching_scholarships_for_profile(
            client=es,
            user_profile=user_profile,
            index=collection,
            collection=collection,
            size=size,
            offset=offset,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Đã xảy ra lỗi nội bộ: {str(e)}",
        )
    finally:
        es.close()


@router.get(
    "/interests/{uid}",
    response_model=Dict[str, Any],
    summary="Get user's scholarship interests (Protected)",
    description="Return the list of scholarship interests. User can only access their own data.",
)
async def get_scholar_interests(
    uid: str,
    current_user: AuthenticatedUser = Depends(verify_firebase_user)
):
    require_user_ownership(current_user, uid)
    
    profile = get_profile(uid)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    interests = profile.get("scholar_interests", [])
    return {"uid": uid, "interests": interests}


@router.post(
    "/interests/{uid}/add",
    response_model=Dict[str, Any],
    summary="Add a new scholarship interest (Protected)",
    description="Add a new scholarship to user's interests list. User can only modify their own data."
)
async def add_scholar_interest(
    uid: str,
    interest: ScholarshipInterest = Body(..., description="Scholarship interest to add"),
    current_user: AuthenticatedUser = Depends(verify_firebase_user)
):
    require_user_ownership(current_user, uid)
    
    try:
        # Get current profile
        profile = get_profile(uid)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Get current interests or initialize empty list
        current_interests = profile.get("scholar_interests", [])
        
        # Check for duplicate
        if any(i.get("scholarship_id") == interest.scholarship_id for i in current_interests):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scholarship {interest.scholarship_id} is already in interests"
            )

        # Add new interest
        current_interests.append(interest.model_dump())
        
        # Update profile
        updated_profile = update_profile(uid, {"scholar_interests": current_interests})
        return {"uid": uid, "interests": updated_profile.get("scholar_interests", [])}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add interest: {str(e)}"
        )


@router.put(
    "/interests/{uid}",
    response_model=Dict[str, Any],
    summary="Update a scholarship interest (Protected)",
    description="Partially update a scholarship in user's interests list. User can only modify their own data."
)
async def update_scholar_interest(
    uid: str, 
    interest_data: ScholarshipInterestUpdate = Body(..., description="Partial update payload; include scholarship_id and any fields to change"),
    current_user: AuthenticatedUser = Depends(verify_firebase_user)
):
    require_user_ownership(current_user, uid)
    
    try:
        # Get current profile
        profile = get_profile(uid)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
            
        # Use scholarship_id from the request body and perform a partial merge
        interest = interest_data

        # Get current interests
        current_interests = profile.get("scholar_interests", [])
        
        # Find and partially update the interest with matching scholarship_id
        found = False
        for i in range(len(current_interests)):
            if current_interests[i].get("scholarship_id") == interest.scholarship_id:
                # Merge existing dict with only provided fields
                update_fields = interest.model_dump(exclude_unset=True)
                merged = {**current_interests[i], **update_fields}
                current_interests[i] = merged
                found = True
                break
                
        if not found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scholarship {interest.scholarship_id} not found in interests"
            )
            
        # Update profile
        updated_profile = update_profile(uid, {"scholar_interests": current_interests})
        return {"uid": uid, "interests": updated_profile.get("scholar_interests", [])}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update interest: {str(e)}"
        )


@router.delete(
    "/interests/{uid}/{scholarship_id}",
    response_model=Dict[str, Any],
    summary="Remove a scholarship interest (Protected)",
    description="Remove a specific scholarship from user's interests list. User can only modify their own data."
)
async def delete_scholar_interest(
    uid: str,
    scholarship_id: str,
    current_user: AuthenticatedUser = Depends(verify_firebase_user)
):
    require_user_ownership(current_user, uid)
    
    try:
        # Get current profile
        profile = get_profile(uid)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Get current interests
        current_interests = profile.get("scholar_interests", [])
        
        # Remove interest with matching scholarship_id
        new_interests = [i for i in current_interests if i.get("scholarship_id") != scholarship_id]
        
        if len(new_interests) == len(current_interests):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scholarship {scholarship_id} not found in interests"
            )
            
        # Update profile
        updated_profile = update_profile(uid, {"scholar_interests": new_interests})
        return {"uid": uid, "interests": updated_profile.get("scholar_interests", [])}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete interest: {str(e)}"
        )


@router.get(
    "/applications/{uid}",
    response_model=Dict[str, Any],
    summary="Get user's scholarship applications (Protected)",
    description="Return the list of scholarship applications. User can only access their own data.",
)
async def get_scholar_applications(
    uid: str,
    current_user: AuthenticatedUser = Depends(verify_firebase_user)
):
    require_user_ownership(current_user, uid)
    
    profile = get_profile(uid)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    applications = profile.get("scholar_applications", [])
    return {"uid": uid, "applications": applications}


@router.post(
    "/applications/{uid}/add",
    response_model=Dict[str, Any],
    summary="Add a new scholarship application (Protected)",
    description="Add a new scholarship application to user's profile. User can only modify their own data.",
)
async def add_scholar_application(
    uid: str,
    application: ScholarshipApplication = Body(..., description="Scholarship application to add"),
    current_user: AuthenticatedUser = Depends(verify_firebase_user)
):
    require_user_ownership(current_user, uid)
    
    try:
        profile = get_profile(uid)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        current_apps = profile.get("scholar_applications", [])

        if any(i.get("scholarship_id") == application.scholarship_id for i in current_apps):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scholarship {application.scholarship_id} is already in applications",
            )

        current_apps.append(application.model_dump())

        updated_profile = update_profile(uid, {"scholar_applications": current_apps})
        return {"uid": uid, "applications": updated_profile.get("scholar_applications", [])}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add application: {str(e)}",
        )


@router.put(
    "/applications/{uid}",
    response_model=Dict[str, Any],
    summary="Update a scholarship application (Protected)",
    description="Partially update a scholarship application. User can only modify their own data.",
)
async def update_scholar_application(
    uid: str,
    application_data: ScholarshipApplicationUpdate = Body(
        ..., description="Partial update payload; include scholarship_id and any fields to change"
    ),
    current_user: AuthenticatedUser = Depends(verify_firebase_user)
):
    require_user_ownership(current_user, uid)
    
    try:
        profile = get_profile(uid)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        app_update = application_data
        current_apps = profile.get("scholar_applications", [])

        found = False
        for i in range(len(current_apps)):
            if current_apps[i].get("scholarship_id") == app_update.scholarship_id:
                update_fields = app_update.model_dump(exclude_unset=True)
                merged = {**current_apps[i], **update_fields}
                current_apps[i] = merged
                found = True
                break

        if not found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scholarship {app_update.scholarship_id} not found in applications",
            )

        updated_profile = update_profile(uid, {"scholar_applications": current_apps})
        return {"uid": uid, "applications": updated_profile.get("scholar_applications", [])}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update application: {str(e)}",
        )


@router.delete(
    "/applications/{uid}/{scholarship_id}",
    response_model=Dict[str, Any],
    summary="Remove a scholarship application (Protected)",
    description="Remove a specific scholarship application. User can only modify their own data.",
)
async def delete_scholar_application(
    uid: str,
    scholarship_id: str,
    current_user: AuthenticatedUser = Depends(verify_firebase_user)
):
    require_user_ownership(current_user, uid)
    
    try:
        profile = get_profile(uid)
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        current_apps = profile.get("scholar_applications", [])
        new_apps = [i for i in current_apps if i.get("scholarship_id") != scholarship_id]

        if len(new_apps) == len(current_apps):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scholarship {scholarship_id} not found in applications",
            )

        updated_profile = update_profile(uid, {"scholar_applications": new_apps})
        return {"uid": uid, "applications": updated_profile.get("scholar_applications", [])}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete application: {str(e)}",
        )
