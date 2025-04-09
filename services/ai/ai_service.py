from services.ai.ai_service_factory import create_ai_service

_ai_service = create_ai_service()


async def ask_ai(user_id, user_question):

    non_quad_keywords = [
        'код', 'програм', 'бот', 'платіж', 'розробк', 'пиши', 'напиши',
        'telegram', 'python', 'javascript', 'html', 'script', 'платежн',
        'aiogram', 'api', 'система', 'функц', 'createbot'
    ]

    # Проверяем, является ли вопрос не связанным с квадроциклами
    if any(keyword in user_question.lower() for keyword in non_quad_keywords):
        return "Я можу допомогти тільки з вибором квадроциклу. Якщо у вас є питання щодо моделей, характеристик або оформлення замовлення - із задоволенням відповім!"

    try:
        response = await _ai_service.generate_response(user_id, user_question)
        return response
    except Exception as e:
        clear_user_context(user_id)
        error_message = f"Сталася помилка при зверненні до AI: {str(e)}"
        print(f"Gemini API error: {str(e)}")
        return error_message


def clear_user_context(user_id):

    _ai_service.clear_context(user_id)