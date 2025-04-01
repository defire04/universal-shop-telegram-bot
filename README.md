# Quad Bike Shop Telegram Bot (aiogram)

This repository contains a Telegram bot for selling quad bikes (ATVs) using **aiogram 3.x**. It provides a dynamic product catalog, a shopping cart flow, an order checkout process, and an admin panel for managing products and viewing orders.


## Key Features

- **Dynamic Catalog**  
  - Multiple brands, added via the admin panel  
  - Products can have names, prices, brands, and photo URLs

- **Shopping Cart**  
  - Users can adjust the quantity before adding an item to the cart  
  - The bot tracks items for each user in a dedicated cart

- **Order Checkout**  
  - Collects user’s full name, phone number, comment, and delivery preferences (e.g., Nova Poshta, UkrPoshta, Courier, or Pickup)  
  - Stores the final order in an SQLite database

- **Admin Panel**  
  - Add products by specifying name, price, brand, and photo URL  
  - List all products (with IDs) and remove products by ID  
  - View orders (with user contact info, full name, address/delivery details)  
  - Show basic statistics (number of orders, total revenue)

- **User-Friendly Interface**  
  - ReplyKeyboard for quick commands (Catalog, Cart, My Orders, Admin Menu if the user is an admin)  
  - InlineKeyboard for in-message navigation (selecting brands, adding to cart, confirming orders, etc.)  
  - Optional sticker usage, random greetings, and friendlier messages

## System Requirements

- **Python 3.12**
- **aiogram 3.18.0** (or similar 3.x version)
- **SQLite** for data storage (bundled with Python)

## Project Structure
 ```bash
quad-bike-shop-aiogram/
├── bot.py
├── requirements.txt
├── Dockerfile
├── data/
│   ├── config.py
│   └── db.py
├── repositories/
│   ├── product_repository.py
│   └── order_repository.py
│   └── user_repository
├── services/
│   ├── product_service.py
│   └── order_service.py
│   └── user_service.py
├── keyboards/
│   ├── inline.py
│   └── reply.py
├── handlers/
│   ├── user_menu.py
│   ├── cart.py
│   ├── admin_menu.py
│   └── fallback.py
└── ...
 ```
## Installation

1. **Clone the repository**:
```bash
  git clone -b quad-bike-shop-aiogram --single-branch https://github.com/defire04/universal-shop-telegram-bot.git quad-bike-shop-aiogram
  ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your bot token** in `data/config.py`:
   ```python
   BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
   ```


## Running the Bot

```bash
python bot.py
```

In Telegram, type `/start` to interact with your bot.

## Docker Usage

If you prefer Docker, use the provided **Dockerfile**:

```bash
docker build -t quad-bike-shop-aiogram .
docker run -it --rm quad-bike-shop-aiogram
```

Adjust the `BOT_TOKEN` by editing `data/config.py` or using an environment variable approach before building.

## Usage

* **Regular users**:
   * `/start` for a friendly greeting
   * **Catalog**: see a list of brands, choose products, add to cart
   * **Cart**: view items, clear, or finalize an order by providing personal info and delivery preferences
   * **My Orders**: check past orders

* **Admins**:
   * `/admin` or "Адмін-меню" (if `ADMIN_IDS` includes the user ID)
   * Add products (`Name|Price|Brand|PhotoURL`)
   * Remove products by ID
   * View orders (with contact info)
   * Basic stats (number of orders, total sum)



# Structure plan for the admin folder:
admin/
├── __init__.py         - Exports the router and initializes handlers
├── router.py           - Main router definition and shared variables
├── product_manage.py   - Product management (add, list, delete)
├── order_manage.py     - Orders listing and statistics
└── state.py            - AdminStates definition

# Structure plan for the cart folder:
cart/
├── __init__.py         - Exports the router and initializes handlers
├── router.py           - Main router definition and shared variables
├── product_view.py     - Product view and quantity handlers
├── cart_management.py  - Cart view and management (clear, etc.)
├── order_process.py    - Order processing and payment
└── state.py            - OrderStates definition

# Structure plan for the user folder:
users/
├── __init__.py - Exports the router and initializes handlers
├── router.py - Main router definition and shared variables
├── start.py - Start command and greeting handlers
├── main_menu.py - Main menu navigation
├── catalog.py - Catalog browsing and brand selection
├── orders.py - Order history viewing 
└── admin_access.py - Admin menu access check