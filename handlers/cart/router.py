from typing import Dict

from aiogram import Router

cart_router = Router()

user_carts: Dict[int, Dict[int, int]] = {}
temp_quantities: Dict[tuple, int] = {}
user_flow: Dict[int, Dict[str, str]] = {}
