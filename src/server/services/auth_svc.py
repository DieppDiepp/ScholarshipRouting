from typing import Optional, Dict, Any
from firebase_admin import auth as firebase_auth, firestore
from services.firestore_svc import save_with_id, get_one_raw


def _ensure_user_in_firestore(uid: str, user_doc: Dict[str, Any]) -> None:
    """
    Đảm bảo user tồn tại trong Firestore collection 'users'.
    Nếu chưa có thì tạo mới.
    """
    profile = get_one_raw("users", uid)
    if profile:
        return
    save_with_id("users", uid, user_doc)


def register_user(
    email: str,
    password: str,
    display_name: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Tạo user mới trong Firebase Authentication + lưu vào Firestore collection 'users'.
    extra_fields: chứa các field bổ sung (thông tin cá nhân, học bổng, CV...).
    """
    user = firebase_auth.create_user(
        email=email,
        password=password,
        display_name=display_name,
    )

    user_doc: Dict[str, Any] = {
        "email": email,
        "display_name": display_name,
        "provider": "password",
    }
    if extra_fields:
        user_doc.update(extra_fields)

    save_with_id("users", user.uid, user_doc)

    return {
        "uid": user.uid,
        "email": email,
        "display_name": display_name,
    }


def verify_token(id_token: str) -> Optional[Dict]:
    """
    Xác thực Firebase ID token (FE gửi lên sau khi login).
    Nếu user mới login lần đầu (Google/Email) thì đồng bộ vào Firestore.
    """
    try:
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception:
        return None

    uid = decoded["uid"]
    email = decoded.get("email")
    display_name = decoded.get("name") or decoded.get("displayName")
    provider = decoded.get("firebase", {}).get("sign_in_provider")

    user_doc = {
        "email": email,
        "display_name": display_name,
        "provider": provider,
    }

    _ensure_user_in_firestore(uid, user_doc)

    return decoded


# ======================
# Profile Management
# ======================

def get_profile(uid: str) -> Optional[Dict[str, Any]]:
    """
    Lấy profile user từ Firestore.
    """
    return get_one_raw("users", uid)


def update_profile(uid: str, fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật profile user trong Firestore (merge fields mới vào).
    """
    db = firestore.client()
    ref = db.collection("users").document(uid)

    # chỉ update những field được gửi lên
    ref.set(fields, merge=True)

    return ref.get().to_dict()
