

from repositories import user_repository

def ensure_user_exists(user_id, full_name):
    user = user_repository.get_user_by_id(user_id)
    if not user:
        user_repository.create_user(user_id, full_name)

def get_user_by_id(user_id):
    return user_repository.get_user_by_id(user_id)
