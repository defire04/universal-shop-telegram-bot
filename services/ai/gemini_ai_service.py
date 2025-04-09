import google.generativeai as genai

from data.config import GEMINI_API_KEY
from services.ai.ai_context_manager import AIContextManager
from services.ai.base_ai_service import BaseAIService

from services.product_service import list_all_products, get_top_products, get_all_brands
from services.user_service import get_user_by_id
from services.order_service import get_user_orders


class GeminiAIService(BaseAIService):
    def __init__(self, model_name="gemini-2.0-flash", max_context_length=10):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = model_name
        self.context_manager = AIContextManager(max_context_length)

    def _get_user_info(self, user_id):
            user = get_user_by_id(user_id)
            user_name = 'Невідомий користувач'
            if user and 'full_name' in user:
                user_name = user['full_name']

            orders = get_user_orders(user_id)
            top_products = get_top_products(3)

            user_info = f"""
    # ІНФОРМАЦІЯ ПРО КОРИСТУВАЧА
    - ID: {user_id}
    - Ім'я: {user_name}
    """

            if orders and len(orders) > 0:
                user_info += "\n# ІСТОРІЯ ЗАМОВЛЕНЬ КОРИСТУВАЧА\n"
                for order in orders[:3]:
                    if 'id' in order and 'total_price' in order and 'created_at' in order:
                        user_info += f"- Замовлення #{order['id']}: сума {order['total_price']} грн, створено {order['created_at']}\n"
            else:
                user_info += "\n# ІСТОРІЯ ЗАМОВЛЕНЬ КОРИСТУВАЧА\n- У користувача ще немає замовлень\n"

            if top_products and len(top_products) > 0:
                user_info += "\n# ПОПУЛЯРНІ ТОВАРИ\n"
                for product in top_products:
                    if 'name' in product and 'brand' in product and 'price' in product and 'id' in product:
                        user_info += f"- ID: {product['id']}, {product['name']} ({product['brand']}): {product['price']} грн\n"
                        if 'description' in product and product['description']:
                            short_desc = product['description'][:100] + '...' if len(product['description']) > 100 else \
                            product['description']
                            user_info += f"  Опис: {short_desc}\n"
            else:
                user_info += "\n# ПОПУЛЯРНІ ТОВАРИ\n- Немає популярних товарів\n"

            return user_info

    def _get_products_info(self):
        products = list_all_products()

        if not products:
            return "В каталозі наразі немає товарів."

        products_text = "УВАГА! В нашому магазині наразі доступні тільки наступні моделі квадроциклів:\n\n"

        for product in products:
            product_dict = dict(product)

            description = product_dict.get('description', "Опис відсутній")

            products_text += (
                f"## Бренд: {product_dict.get('brand', 'Без бренду')}\n"
                f"- ID: {product_dict.get('id', 'Невідомо')}\n"
                f"  Назва: {product_dict.get('name', 'Без назви')}\n"
                f"  Ціна: {product_dict.get('price', 'Ціна не вказана')} грн\n"
                f"  Опис: {description}\n\n"
            )

        products_text += "ВАЖЛИВО! Рекомендуй товари ТІЛЬКИ з цього списку і надавай точну інформацію про них!"
        return products_text

    def _build_system_instruction(self, user_id):
        from data.ai_instructions import SYSTEM_INSTRUCTIONS, PRODUCTS_CONTEXT_TEMPLATE, BRANDS_TEMPLATE

        available_brands = get_all_brands()
        brands_list = ", ".join(available_brands) if available_brands else "Немає доступних брендів"

        brands_info = BRANDS_TEMPLATE.format(brands_list=brands_list)

        user_info = self._get_user_info(user_id)
        products_info = self._get_products_info()
        products_context = PRODUCTS_CONTEXT_TEMPLATE.format(products_info=products_info)

        full_instruction = f"{SYSTEM_INSTRUCTIONS}\n\n{brands_info}\n\n{user_info}\n\n{products_context}"

        return full_instruction

    async def generate_response(self, user_id, user_message, user_data=None):
        try:
            system_instruction = self._build_system_instruction(user_id)

            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )

            product_keywords = ['квадроцикл', 'товар', 'модель', 'бренд', 'каталог', 'ціна']
            is_product_query = any(keyword in user_message.lower() for keyword in product_keywords)

            context = self.get_context_for_user(user_id)

            if is_product_query or not context or len(context) == 0:
                response = model.generate_content(user_message)
            else:
                chat = model.start_chat(history=context)
                response = chat.send_message(user_message)

            response_text = response.text

            self.update_context(user_id, user_message, response_text)

            return response_text

        except Exception as e:
            error_message = f"Сталася помилка при зверненні до AI: {str(e)}"
            print(f"Gemini API error: {str(e)}")
            return error_message

    def get_context_for_user(self, user_id):
        return self.context_manager.get_context(user_id)

    def update_context(self, user_id, message, response):
        self.context_manager.add_exchange(user_id, message, response)

    def clear_context(self, user_id):
        self.context_manager.clear_context(user_id)