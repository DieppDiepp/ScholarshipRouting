"""
Example User Profile cho testing
Chỉ giữ 1 profile mẫu để test cơ bản
"""

# Profile mẫu: Sinh viên IT muốn học Master
SAMPLE_PROFILE = {
    "name": "Duong Dac Ngoc Trieu Minh",
    "age": 22,
    "gender": "Male",
    "nationality": "Vietnam",
    "current_degree": "Bachelor",
    "gpa": 3.5,
    "field_of_study": "Computer Science",
    "university": "HCMC University of Technology",
    "language_certificates": [
        {"type": "IELTS", "score": 7.0}
    ],
    "work_experience_years": 1,
    "target_degree": "Master",
    "target_field": "Data Science",
    "target_countries": ["Turkey", "Hungary"],
    "budget": "full_scholarship"
}


def get_sample_profile() -> dict:
    """
    Lấy profile mẫu để test
    
    Returns:
        Dict chứa profile data
    """
    return SAMPLE_PROFILE.copy()


def validate_profile(profile: dict) -> bool:
    """
    Validate profile data
    
    Args:
        profile: Dict chứa profile data
        
    Returns:
        True nếu hợp lệ, False nếu không
    """
    if not profile:
        return False
        
    required_fields = ["name", "current_degree", "target_degree", "target_field"]
    
    for field in required_fields:
        if field not in profile or not profile[field]:
            print(f"✗ Missing required field: {field}")
            return False
    
    # Validate GPA range
    if profile.get("gpa") and not (0.0 <= profile["gpa"] <= 4.0):
        print(f"✗ Invalid GPA: {profile['gpa']} (must be 0.0-4.0)")
        return False
    
    return True


if __name__ == "__main__":
    print("\n=== SAMPLE PROFILE ===")
    profile = get_sample_profile()
    print(f"Name: {profile['name']}")
    print(f"Current: {profile['current_degree']} in {profile['field_of_study']}")
    print(f"Target: {profile['target_degree']} in {profile['target_field']}")
    print(f"GPA: {profile['gpa']}")
    print(f"Countries: {', '.join(profile['target_countries'])}")
    print(f"\nValid: {validate_profile(profile)}")
