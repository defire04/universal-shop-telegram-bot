from repositories import feedback_repository

def save_new_feedback(user_id, username, full_name, feedback_text):
    return feedback_repository.save_feedback(user_id, username, full_name, feedback_text)

def get_all_feedback():
    return feedback_repository.get_all_feedback()

def get_feedback_page(page, page_size):
    return feedback_repository.get_feedback_page(page, page_size)

def get_feedback_count():
    return feedback_repository.get_feedback_count()

def get_user_feedback(user_id):
    return feedback_repository.get_feedback_by_user_id(user_id)

def get_feedback(feedback_id):
    return feedback_repository.get_feedback_by_id(feedback_id)