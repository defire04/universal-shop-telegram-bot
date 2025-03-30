# Fish Order Telegram Bot

This is a Telegram bot for ordering decorative fish food. It features a dynamic catalog of multiple brands, a shopping cart system, and an extended checkout flow (including full name, phone number, comment, and multiple delivery options). It also provides an admin panel to add or remove products, view the product list, track orders, and display basic statistics.

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
- **pyTelegramBotAPI 4.26.0**
- SQLite (bundled with Python)

## Project Structure
 ```bash
fish-shop-telebot/
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
   git clone -b fish-shop-telebot --single-branch https://github.com/defire04/universal-shop-telegram-bot.git fish-shop-telebot
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
docker build -t fish-shop-telebot .
docker run -it --rm fish-shop-telebot
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
