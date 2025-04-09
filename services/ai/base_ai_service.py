from abc import ABC, abstractmethod


class BaseAIService(ABC):

    @abstractmethod
    async def generate_response(self, user_id, user_message, user_data=None):
        pass

    @abstractmethod
    def get_context_for_user(self, user_id):
        pass

    @abstractmethod
    def update_context(self, user_id, message, response):
        pass

    @abstractmethod
    def clear_context(self, user_id):
        pass