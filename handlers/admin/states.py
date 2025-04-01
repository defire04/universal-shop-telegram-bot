from aiogram.fsm.state import State, StatesGroup

class AdminActions(StatesGroup):
    waiting_for_product_info = State()
    waiting_for_product_id = State()