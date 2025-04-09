# Universal Shop Telegram Bot

A flexible, feature-rich Telegram bot built with **aiogram 3.x** that can be easily adapted for any type of online store. Currently configured as a Quad Bike Shop, but can be customized for any product category by modifying text constants and AI instructions.

## Features

### Customer Features
- **Dynamic Product Catalog**
  - Browse products by brand/category
  - Detailed product pages with images, descriptions, and pricing
  - Navigation between products with previous/next controls

- **Smart Shopping Cart**
  - Add products with quantity selection
  - View, edit, and clear cart contents
  - Real-time total calculation

- **Comprehensive Order System**
  - Multi-step checkout process with validation
  - Multiple delivery options (Courier, Nova Poshta, UkrPoshta, Pickup)
  - Multiple payment methods (Pay now, Pay on delivery)
  - Order confirmation and history

- **AI Assistance**
  - Integrated AI helper powered by Google's Gemini
  - Product recommendations based on user preferences
  - Smart responses to product inquiries
  - Contextual conversation memory

- **Customer Support**
  - Contact information with social media links
  - Feedback collection system
  - Help documentation

### Admin Features
- **Product Management**
  - Add new products with detailed information
  - List, edit, and remove products
  - Organize products by brand/category

- **Order Management**
  - View all orders with detailed customer information
  - Paginated order listing
  - Track payment status

- **Customer Feedback**
  - View and manage customer feedback
  - Paginated feedback listing

- **Analytics**
  - Basic statistics on orders and revenue
  - Most popular products tracking

## Technology Stack

- **Python 3.12**
- **aiogram 3.18.0** (Telegram Bot Framework)
- **SQLite** for data storage
- **Google Gemini API** for AI assistant functionality
- **Docker** support for containerization

## Project Structure

```
universal-shop-bot/
├── bot.py                 # Main entry point
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Multi-container setup
├── requirements.txt       # Dependencies
│
├── data/                  # Configuration and constants
│   ├── ai_instructions.py # AI assistant instructions
│   ├── bot_texts.py       # Customizable text messages
│   ├── config.py          # Bot configuration
│   └── db.py              # Database initialization
│
├── handlers/              # Telegram message handlers
│   ├── admin/             # Admin panel handlers
│   ├── ai/                # AI assistant handlers
│   ├── cart/              # Shopping cart handlers
│   ├── contact/           # Contact & feedback handlers
│   ├── user/              # User interaction handlers
│   └── fallback.py        # Fallback handler
│
├── keyboards/             # UI components
│   ├── inline.py          # Inline keyboard layouts
│   └── reply.py           # Reply keyboard layouts
│
├── repositories/          # Database access layer
│   ├── feedback_repository.py
│   ├── order_repository.py
│   ├── product_repository.py
│   └── user_repository.py
│
├── services/              # Business logic layer
│   ├── ai/                # AI service components
│   ├── feedback_service.py
│   ├── order_service.py
│   ├── product_service.py
│   └── user_service.py
│
└── utils/                 # Utility functions
    └── safe_dict.py
```

## Customization

This bot is designed to be universally adaptable for any type of online store:

1. **Change Product Type**: Modify text constants in `data/bot_texts.py` to match your product category
2. **Customize AI Assistant**: Update instructions in `data/ai_instructions.py` to reflect your product knowledge
3. **Adapt Database**: The schema is flexible enough for various product types
4. **Modify UI**: Keyboards can be customized in `keyboards/` directory

The architecture separates concerns into:
- Repositories (data access)
- Services (business logic)
- Handlers (bot interaction)

This makes it easy to modify any layer without affecting others.

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/username/universal-shop-bot.git
cd universal-shop-bot
```

2. **Set up environment variables**:
Create a `.env` file with:
```
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=comma,separated,admin,ids
GEMINI_API_KEY=your_google_gemini_api_key
PAYMENT_TOKEN=your_payment_token
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the bot**:
```bash
python bot.py
```

## Docker Deployment

For containerized deployment:

```bash
docker-compose up -d
```

This will start:
- The bot container
- An SQLiteBrowser container for database management

## Usage

### For Customers
- `/start` - Begin interaction with the bot
- `/help` - View available commands
- `/catalog` - Browse products
- `/cart` - View shopping cart
- `/orders` - View order history
- `/contact` - View contact information
- `/feedback` - Leave feedback
- `/ai` - Interact with AI assistant

### For Administrators
- `/admin` - Access admin panel
- Add products with format: `Name|Price|Brand|Description|PhotoURL`
- View orders, statistics, and customer feedback

## License

MIT License