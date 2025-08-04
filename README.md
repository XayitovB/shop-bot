# Telegram E-Commerce Bot (Aiogram 3)

A simple Telegram e-commerce bot built with **aiogram 3** that allows users to browse products, add them to cart, and checkout.

## Features

- 🛍️ Browse available products
- 🛒 Add/remove items from cart
- 📦 Track inventory in real-time
- 💳 Simple checkout process
- ℹ️ Help and navigation system
- 🔄 Interactive inline keyboards

## Setup Instructions

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Save the bot token you receive

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file and replace `your_telegram_bot_token_here` with your actual bot token:
   ```
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 4. Run the Bot

```bash
python bot_aiogram3.py
```

## Bot Commands

- `/start` - Start the bot and show main menu

## Bot Features

### Main Menu
- **🛍️ Browse Products** - View all available items
- **🛒 View Cart** - Check your shopping cart
- **ℹ️ Help** - Get help information

### Product Browsing
- View product details (name, price, stock, description)
- Add products to cart
- Real-time stock updates

### Shopping Cart
- View all items in cart with quantities
- Remove items from cart
- See total price
- Proceed to checkout

### Checkout
- Complete purchase simulation
- Order confirmation
- Cart clearing after successful purchase

## Code Structure

### Key Components

1. **Product Management**: Hardcoded product catalog with stock tracking
2. **User Cart System**: In-memory cart storage per user
3. **Inline Keyboards**: Modern aiogram 3 keyboard builders
4. **Callback Handlers**: Event-driven interaction handling

### Modern Aiogram 3 Features Used

- `Router` for organizing handlers
- `F` (Magic Filter) for callback data filtering
- `InlineKeyboardBuilder` for dynamic keyboard creation
- Async/await pattern throughout
- Type hints for better code quality

## Database Integration

This example uses in-memory storage. For production use, consider integrating:

- **SQLite** for simple deployments
- **PostgreSQL** for production scale
- **Redis** for session management

## Deployment Options

- **Local development**: Run directly with Python
- **VPS/Cloud**: Deploy on DigitalOcean, AWS, etc.
- **Docker**: Containerize for easy deployment
- **Heroku**: Simple cloud deployment

## Security Considerations

- Keep bot token secure (use environment variables)
- Implement user authentication for sensitive operations
- Add rate limiting to prevent spam
- Validate all user inputs

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
