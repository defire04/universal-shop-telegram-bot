from aiogram.fsm.state import State, StatesGroup


class FeedbackStates(StatesGroup):
    waiting_for_message = State()