from fastapi import APIRouter, HTTPException
from services.auth_svc import register_user, verify_token, get_profile, update_profile
from dtos.auth_dtos import RegisterRequest, VerifyRequest, UpdateProfileRequest
from typing import Dict, Any

router = APIRouter()

@router.post("/register")
def register(req: RegisterRequest):
    try:
        # lấy toàn bộ field (ngoại trừ email/password/display_name)
        extra_fields = req.dict(exclude={"email", "password", "display_name"}, exclude_unset=True)
        user = register_user(req.email, req.password, req.display_name, extra_fields)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify")
def verify(req: VerifyRequest):
    payload = verify_token(req.id_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload


@router.get("/profile/{uid}")
def get_user_profile(uid: str):
    profile = get_profile(uid)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile


@router.put("/profile/{uid}")
def update_user_profile(uid: str, req: UpdateProfileRequest):
    try:
        fields = req.dict(exclude_unset=True)
        updated = update_profile(uid, fields)
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))