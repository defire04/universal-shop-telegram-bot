import google.generativeai as genai

from data.config import GEMINI_API_KEY
from services.ai.ai_context_manager import AIContextManager
from services.ai.base_ai_service import BaseAIService

from services.product_service import list_all_products, get_top_products, get_all_brands, get_product
from services.user_service import get_user_by_id
from services.order_service import get_user_orders
from utils.safe_dict import safe_dict


class GeminiAIService(BaseAIService):
    def __init__(self, model_name="gemini-2.0-flash", max_context_length=10):
        genai.configure(api_key=GEMINI_API_KEY)
        self.model_name = model_name
        self.context_manager = AIContextManager(max_context_length)



    def _get_user_info(self, user_id):
        try:
            user = get_user_by_id(user_id)
            user_dict = safe_dict(user)

            user_name = user_dict.get("full_name", 'Невідомий користувач')

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
                    order_dict = safe_dict(order)
                    if 'id' in order_dict and 'total_price' in order_dict and 'created_at' in order_dict:
                        user_info += f"- Замовлення #{order_dict['id']}: сума {order_dict['total_price']} грн, створено {order_dict['created_at']}\n"
            else:
                user_info += "\n# ІСТОРІЯ ЗАМОВЛЕНЬ КОРИСТУВАЧА\n- У користувача ще немає замовлень\n"

            if top_products and len(top_products) > 0:
                user_info += "\n# ПОПУЛЯРНІ ТОВАРИ\n"
                for product in top_products:
                    product_dict = safe_dict(product)
                    if 'name' in product_dict and 'brand' in product_dict and 'price' in product_dict and 'id' in product_dict:
                        user_info += f"- ID: {product_dict['id']}, {product_dict['name']} ({product_dict['brand']}): {product_dict['price']} грн\n"
                        if 'description' in product_dict and product_dict['description']:
                            short_desc = product_dict['description'][:100] + '...' if len(
                                product_dict['description']) > 100 else \
                                product_dict['description']
                            user_info += f"  Опис: {short_desc}\n"
            else:
                user_info += "\n# ПОПУЛЯРНІ ТОВАРИ\n- Немає популярних товарів\n"

            return user_info
        except Exception as e:
            print(f"Error in _get_user_info: {e}")
            return "# ІНФОРМАЦІЯ ПРО КОРИСТУВАЧА\n- Не вдалося отримати інформацію про користувача"

    def _get_products_info(self):
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
            last_product = self.context_manager.get_last_product(user_id)

            # Перевірка, чи йдеться про останній рекомендований товар
            if last_product and ('деталі' in user_message.lower() or 'більше' in user_message.lower() or
                                 'розкажи' in user_message.lower() or 'інформація' in user_message.lower()):
                detailed_product_info = self._get_detailed_product_info(last_product)

                # Генеруємо розширену відповідь про товар
                chat = model.start_chat(history=context)
                response = chat.send_message(f"Розкажи більше про цей товар: {detailed_product_info}")
                response_text = response.text

                # Оновлюємо контекст без повторного збереження товару
                self.context_manager.add_exchange(user_id, user_message, response_text)
                return response_text

            # Якщо це запит про товар або немає контексту, генеруємо нову відповідь
            if is_product_query or not context or len(context) == 0:
                response = model.generate_content(user_message)

                # Намагаємось витягти товар з відповіді
                recommended_product = self._extract_recommended_product(response.text)

                # Оновлюємо контекст з відповіддю та потенційним товаром
                self.context_manager.add_exchange(
                    user_id,
                    user_message,
                    response.text,
                    last_product=recommended_product
                )
            else:
                # Продовження існуючої розмови
                chat = model.start_chat(history=context)
                response = chat.send_message(user_message)

                # Оновлюємо контекст
                self.context_manager.add_exchange(user_id, user_message, response.text)

            response_text = response.text
            return response_text

        except Exception as e:
            error_message = f"Сталася помилка при зверненні до AI: {str(e)}"
            print(f"Gemini API error: {str(e)}")
            return error_message

    def _extract_recommended_product(self, response_text):
        """
        Намагається витягти ID товару з відповіді AI.
        """
        products = list_all_products()
        for product in products:
            product_dict = safe_dict(product)
            product_name = product_dict.get('name', '').lower()
            if product_name in response_text.lower():
                return product_dict

        return None

    def _get_detailed_product_info(self, product):
        """
        Генерує детальний опис товару.
        """
        if not product:
            return "Вибачте, інформація про товар недоступна."

        return (
            f"Детальна інформація про {product.get('name', 'Товар')}:\n"
            f"🏷️ Бренд: {product.get('brand', 'Не вказано')}\n"
            f"💰 Ціна: {product.get('price', 'Не вказано')} грн\n"
            f"📝 Опис: {product.get('description', 'Детальний опис відсутній')}\n"
            f"🖼️ Фото: {product.get('photo_url', 'Немає фото')}"
        )

    def get_context_for_user(self, user_id):
        return self.context_manager.get_context(user_id)

    def update_context(self, user_id, message, response):
        self.context_manager.add_exchange(user_id, message, response)

    def clear_context(self, user_id):
        self.context_manager.clear_context(user_id)