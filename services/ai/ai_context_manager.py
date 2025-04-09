class AIContextManager:
    def __init__(self, max_context_length=10):
        self.user_contexts = {}
        self.max_context_length = max_context_length

    def get_context(self, user_id):
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []
        return self.user_contexts[user_id]

    def add_exchange(self, user_id, user_message, assistant_response):
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []

        self.user_contexts[user_id].append({
            "parts": [{"text": user_message}],
            "role": "user"
        })

        self.user_contexts[user_id].append({
            "parts": [{"text": assistant_response}],
            "role": "model"
        })

        if len(self.user_contexts[user_id]) > self.max_context_length * 2:
            self.user_contexts[user_id] = self.user_contexts[user_id][-(self.max_context_length * 2):]

    def clear_context(self, user_id):
        if user_id in self.user_contexts:
            self.user_contexts[user_id] = []