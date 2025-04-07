import google.generativeai as genai

from data.ai_instructions import SYSTEM_INSTRUCTIONS, PRODUCTS_CONTEXT_TEMPLATE
from data.config import GEMINI_API_KEY
from services.product_service import list_all_products

genai.configure(api_key=GEMINI_API_KEY)

def get_products_info():

    products = list_all_products()
    if not products:
        return "В каталозі наразі немає товарів."

    products_text = ""
    for product in products:
        product_info = (
            f"- ID: {product['id']}\n"
            f"  Назва: {product['name']}\n"
            f"  Бренд: {product['brand']}\n"
            f"  Ціна: {product['price']} грн\n"
            f"  Опис: {product.get('description', 'Опис відсутній')}\n"
        )
        products_text += product_info + "\n"

    return products_text


def get_gemini_model():
    products_info = get_products_info()
    products_context = PRODUCTS_CONTEXT_TEMPLATE.format(products_info=products_info)

    full_instructions = SYSTEM_INSTRUCTIONS + "\n\n" + products_context

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=full_instructions
    )

    return model


async def ask_gemini(user_question):
    try:
        model = get_gemini_model()
        response = model.generate_content(user_question)
        return response.text
    except Exception as e:
        return f"Сталася помилка при зверненні до AI: {str(e)}"
