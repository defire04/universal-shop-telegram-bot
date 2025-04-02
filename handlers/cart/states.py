from typing import Dict

from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    full_name = State()
    phone = State()
    comment = State()
    delivery_method = State()
    address = State()
    payment_method = State()


user_carts: Dict[int, Dict[int, int]] = {}
temp_quantities: Dict[tuple, int] = {}
user_flow: Dict[int, Dict[str, str]] = {}
