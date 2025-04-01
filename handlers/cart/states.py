from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    full_name = State()
    phone = State()
    comment = State()
    delivery_method = State()
    address = State()
    payment_method = State()