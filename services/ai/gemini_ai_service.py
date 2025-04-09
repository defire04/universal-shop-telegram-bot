import google.generativeai as genai

from data.ai_instructions import BRANDS_TEMPLATE, PRODUCTS_CONTEXT_TEMPLATE, SYSTEM_INSTRUCTIONS
from data.config import GEMINI_API_KEY
from services.ai.ai_context_manager import AIContextManager
from services.ai.base_ai_service import BaseAIService

from services.product_service import list_all_products, get_top_products, get_all_brands
from services.user_service import get_user_by_id
from services.order_service import get_user_orders
from utils.safe_dict import safe_dict


class GeminiAIService(BaseAIService):
    def __init__(self, model_name="gemini-2.0-flash", max_context_length=10):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = model_name
        self.context_manager = AIContextManager(max_context_length)

    def _format_order_history(self, orders):
        if not orders:
            return "\n# ІСТОРІЯ ЗАМОВЛЕНЬ КОРИСТУВАЧА\n- У користувача ще немає замовлень\n"

        order_history = "\n# ІСТОРІЯ ЗАМОВЛЕНЬ КОРИСТУВАЧА\n"
        for order in orders[:3]:
            order_dict = safe_dict(order)
            if all(key in order_dict for key in ['id', 'total_price', 'created_at']):
                order_history += (
                    f"- Замовлення #{order_dict['id']}: "
                    f"сума {order_dict['total_price']} грн, "
                    f"створено {order_dict['created_at']}\n"
                )
        return order_history

    def _format_top_products(self, top_products):
        if not top_products:
            return "\n# ПОПУЛЯРНІ ТОВАРИ\n- Немає популярних товарів\n"

        top_products_info = "\n# ПОПУЛЯРНІ ТОВАРИ\n"
        for product in top_products:
            product_dict = safe_dict(product)
            if all(key in product_dict for key in ['name', 'brand', 'price', 'id']):
                top_products_info += (
                    f"- ID: {product_dict['id']}, "
                    f"{product_dict['name']} ({product_dict['brand']}): "
                    f"{product_dict['price']} грн\n"
                )

                if 'description' in product_dict and product_dict['description']:
                    short_desc = product_dict['description'][:100] + '...' if len(
                        product_dict['description']) > 100 else product_dict['description']
                    top_products_info += f"  Опис: {short_desc}\n"
        return top_products_info

    def _build_user_profile(self, user_id):
        try:
            user = get_user_by_id(user_id)
            user_dict = safe_dict(user)

            user_name = user_dict.get("full_name", 'Невідомий користувач')
            orders = get_user_orders(user_id)
            top_products = get_top_products(3)

            user_info = (
                f"# ІНФОРМАЦІЯ ПРО КОРИСТУВАЧА\n"
                f"- ID: {user_id}\n"
                f"- Ім'я: {user_name}\n"
            )
            user_info += self._format_order_history(orders)
            user_info += self._format_top_products(top_products)

            return user_info
        except Exception as e:
            print(f"Error in _build_user_profile: {e}")
            return "# ІНФОРМАЦІЯ ПРО КОРИСТУВАЧА\n- Не вдалося отримати інформацію про користувача"

    def _generate_products_catalog(self):
        products = list_all_products()

        if not products:
            return "В каталозі наразі немає товарів."

        products_text = "УВАГА! В нашому магазині наразі доступні тільки наступні моделі квадроциклів:\n\n"

        for product in products:
            product_dict = safe_dict(product)
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

    def _prepare_system_instruction(self, user_id):
        available_brands = get_all_brands()
        brands_list = ", ".join(available_brands) if available_brands else "Немає доступних брендів"

        brands_info = BRANDS_TEMPLATE.format(brands_list=brands_list)
        user_info = self._build_user_profile(user_id)
        products_info = self._generate_products_catalog()
        products_context = PRODUCTS_CONTEXT_TEMPLATE.format(products_info=products_info)

        return f"{SYSTEM_INSTRUCTIONS}\n\n{brands_info}\n\n{user_info}\n\n{products_context}"

    def _find_recommended_product(self, response_text):
        products = list_all_products()
        for product in products:
            product_dict = safe_dict(product)
            product_name = product_dict.get('name', '').lower()
            if product_name in response_text.lower():
                return product_dict
        return None

    def _create_product_details(self, product):
        if not product:
            return "Вибачте, інформація про товар недоступна."

        return (
            f"Детальна інформація про {product.get('name', 'Товар')}:\n"
            f"🏷️ Бренд: {product.get('brand', 'Не вказано')}\n"
            f"💰 Ціна: {product.get('price', 'Не вказано')} грн\n"
            f"📝 Опис: {product.get('description', 'Детальний опис відсутній')}\n"
            f"🖼️ Фото: {product.get('photo_url', 'Немає фото')}"
        )

    async def generate_response(self, user_id, user_message, user_data=None):
        try:
            system_instruction = self._prepare_system_instruction(user_id)

            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )

            product_keywords = ['квадроцикл', 'товар', 'модель', 'бренд', 'каталог', 'ціна']
            is_product_query = any(keyword in user_message.lower() for keyword in product_keywords)

            context = self.get_context_for_user(user_id)
            last_product = self.context_manager.get_last_product(user_id)

            detail_keywords = ['деталі', 'більше', 'розкажи', 'інформація']
            is_detail_request = last_product and any(keyword in user_message.lower() for keyword in detail_keywords)

            if is_detail_request:
                detailed_product_info = self._create_product_details(last_product)
                chat = model.start_chat(history=context)
                response = chat.send_message(f"Розкажи більше про цей товар: {detailed_product_info}")

                self.context_manager.add_exchange(user_id, user_message, response.text)
                return response.text

            if is_product_query or not context or len(context) == 0:
                response = model.generate_content(user_message)
                recommended_product = self._find_recommended_product(response.text)

                self.context_manager.add_exchange(
                    user_id,
                    user_message,
                    response.text,
                    last_product=recommended_product
                )
            else:
                chat = model.start_chat(history=context)
                response = chat.send_message(user_message)
                self.context_manager.add_exchange(user_id, user_message, response.text)

            return response.text

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