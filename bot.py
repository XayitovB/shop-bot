import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.filters import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Store data (in production, use a proper database)
PRODUCTS = {
    "1": {"name": "Laptop", "price": 999.99, "description": "High-performance laptop", "stock": 10},
    "2": {"name": "Smartphone", "price": 599.99, "description": "Latest smartphone model", "stock": 15},
    "3": {"name": "Headphones", "price": 199.99, "description": "Wireless noise-canceling headphones", "stock": 20},
    "4": {"name": "Tablet", "price": 399.99, "description": "10-inch tablet with stylus", "stock": 8},
    "5": {"name": "Smart Watch", "price": 299.99, "description": "Fitness tracking smartwatch", "stock": 12}
}

# User carts (in production, use a proper database)
USER_CARTS = {}

@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    """Send a message when the command /start is issued."""
    user = message.from_user
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🛍️ Browse Products", callback_data='browse_products'),
        InlineKeyboardButton(text="🛒 View Cart", callback_data='view_cart'),
        InlineKeyboardButton(text="ℹ️ Help", callback_data='help')
    )
    builder.adjust(1)
    
    await message.answer(
        f'Welcome to our E-Store, {user.first_name}! 🛒\n\n'
        'What would you like to do today?',
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == "browse_products")
async def browse_products(callback: CallbackQuery) -> None:
    """Show available products."""
    builder = InlineKeyboardBuilder()
    for product_id, product in PRODUCTS.items():
        builder.add(
            InlineKeyboardButton(
                text=f"{product['name']} - ${product['price']} (Stock: {product['stock']})",
                callback_data=f'product_{product_id}'
            )
        )
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_menu'))

    await callback.message.edit_text(
        '🛍️ **Available Products:**\n\n'
        'Click on any product to view details and add to cart:',
        reply_markup=builder.as_markup(),
        parse_mode='Markdown'
    )

@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery) -> None:
    """Show product details."""
    product_id = callback.data.split('_')[1]
    product = PRODUCTS.get(product_id)
    
    if not product:
        await callback.message.edit_text("Product not found!")
        return
    
    builder = InlineKeyboardBuilder()
    if product['stock'] > 0:
        builder.add(InlineKeyboardButton(text="➕ Add to Cart", callback_data=f'add_to_cart_{product_id}'))
    else:
        builder.add(InlineKeyboardButton(text="❌ Out of Stock", callback_data='out_of_stock'))
    
    builder.row(
        InlineKeyboardButton(text="🛍️ Browse Products", callback_data='browse_products'),
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_menu')
    )
    
    await callback.message.edit_text(
        f'**{product["name"]}**\n\n'
        f'💰 Price: ${product["price"]}\n'
        f'📦 Stock: {product["stock"]}\n'
        f'📝 Description: {product["description"]}',
        reply_markup=builder.as_markup(),
        parse_mode='Markdown'
    )

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery) -> None:
    """Add product to cart."""
    user_id = callback.from_user.id
    product_id = callback.data.split('_')[3]
    
    product = PRODUCTS.get(product_id)
    if not product or product['stock'] <= 0:
        await callback.answer("Sorry, this product is out of stock!", show_alert=True)
        return
    
    # Initialize user cart if it doesn't exist
    if user_id not in USER_CARTS:
        USER_CARTS[user_id] = {}
    
    # Add product to cart
    if product_id in USER_CARTS[user_id]:
        USER_CARTS[user_id][product_id] += 1
    else:
        USER_CARTS[user_id][product_id] = 1
    
    # Decrease stock
    PRODUCTS[product_id]['stock'] -= 1
    
    await callback.answer(f"✅ {product['name']} added to cart!", show_alert=True)
    
    # Show updated product info
    builder = InlineKeyboardBuilder()
    if product['stock'] > 0:
        builder.add(InlineKeyboardButton(text="➕ Add to Cart", callback_data=f'add_to_cart_{product_id}'))
    else:
        builder.add(InlineKeyboardButton(text="❌ Out of Stock", callback_data='out_of_stock'))
    
    builder.row(
        InlineKeyboardButton(text="🛍️ Browse Products", callback_data='browse_products'),
        InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_menu')
    )
    
    await callback.message.edit_text(
        f'**{product["name"]}**\n\n'
        f'💰 Price: ${product["price"]}\n'
        f'📦 Stock: {product["stock"]}\n'
        f'📝 Description: {product["description"]}',
        reply_markup=builder.as_markup(),
        parse_mode='Markdown'
    )

@router.callback_query(F.data == "view_cart")
async def view_cart(callback: CallbackQuery) -> None:
    """Show user's cart."""
    user_id = callback.from_user.id
    cart = USER_CARTS.get(user_id, {})
    
    if not cart:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_menu'))
        await callback.message.edit_text(
            "🛒 Your cart is empty!\n\nStart shopping to add items to your cart.",
            reply_markup=builder.as_markup()
        )
        return
    
    cart_text = "🛒 **Your Cart:**\n\n"
    total = 0
    
    builder = InlineKeyboardBuilder()
    for product_id, quantity in cart.items():
        product = PRODUCTS.get(product_id)
        if product:
            item_total = product['price'] * quantity
            total += item_total
            cart_text += f"• {product['name']} x{quantity} - ${item_total:.2f}\n"
            builder.add(InlineKeyboardButton(text=f"➖ Remove {product['name']}", callback_data=f'remove_{product_id}'))
    
    cart_text += f"\n💰 **Total: ${total:.2f}**"
    
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="💳 Checkout", callback_data='checkout'),
        InlineKeyboardButton(text="🛍️ Continue Shopping", callback_data='browse_products')
    )
    builder.row(InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_menu'))
    
    await callback.message.edit_text(cart_text, reply_markup=builder.as_markup(), parse_mode='Markdown')

@router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: CallbackQuery) -> None:
    """Remove product from cart."""
    user_id = callback.from_user.id
    product_id = callback.data.split('_')[1]
    
    if user_id in USER_CARTS and product_id in USER_CARTS[user_id]:
        # Decrease quantity or remove item
        if USER_CARTS[user_id][product_id] > 1:
            USER_CARTS[user_id][product_id] -= 1
        else:
            del USER_CARTS[user_id][product_id]
        
        # Increase stock
        PRODUCTS[product_id]['stock'] += 1
        
        product_name = PRODUCTS.get(product_id, {}).get('name', 'Product')
        await callback.answer(f"✅ {product_name} removed from cart!")
    
    # Show updated cart
    cart = USER_CARTS.get(user_id, {})
    
    if not cart:
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_menu'))
        await callback.message.edit_text(
            "🛒 Your cart is empty!\n\nStart shopping to add items to your cart.",
            reply_markup=builder.as_markup()
        )
        return
    
    cart_text = "🛒 **Your Cart:**\n\n"
    total = 0
    
    builder = InlineKeyboardBuilder()
    for product_id, quantity in cart.items():
        product = PRODUCTS.get(product_id)
        if product:
            item_total = product['price'] * quantity
            total += item_total
            cart_text += f"• {product['name']} x{quantity} - ${item_total:.2f}\n"
            builder.add(InlineKeyboardButton(text=f"➖ Remove {product['name']}", callback_data=f'remove_{product_id}'))
    
    cart_text += f"\n💰 **Total: ${total:.2f}**"
    
    builder.adjust(1)
    builder.row(
        InlineKeyboardButton(text="💳 Checkout", callback_data='checkout'),
        InlineKeyboardButton(text="🛍️ Continue Shopping", callback_data='browse_products')
    )
    builder.row(InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_menu'))
    
    await callback.message.edit_text(cart_text, reply_markup=builder.as_markup(), parse_mode='Markdown')

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery) -> None:
    """Process checkout."""
    user_id = callback.from_user.id
    cart = USER_CARTS.get(user_id, {})
    
    if not cart:
        await callback.answer("Your cart is empty!", show_alert=True)
        return
    
    # Calculate total
    total = 0
    for product_id, quantity in cart.items():
        product = PRODUCTS.get(product_id)
        if product:
            total += product['price'] * quantity
    
    # Clear cart (simulate successful payment)
    USER_CARTS[user_id] = {}
    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_menu'))
    
    await callback.message.edit_text(
        f"✅ **Order Confirmed!**\n\n"
        f"💰 Total Amount: ${total:.2f}\n"
        f"📧 A confirmation email has been sent.\n"
        f"📦 Your order will be delivered in 3-5 business days.\n\n"
        f"Thank you for shopping with us! 🎉",
        reply_markup=builder.as_markup(),
        parse_mode='Markdown'
    )

@router.callback_query(F.data == "help")
async def help_command(callback: CallbackQuery) -> None:
    """Show help information."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Back to Menu", callback_data='back_to_menu'))
    
    help_text = (
        "ℹ️ **How to use this bot:**\n\n"
        "🛍️ **Browse Products** - View all available items\n"
        "🛒 **View Cart** - Check items in your cart\n"
        "➕ **Add to Cart** - Add products you like\n"
        "➖ **Remove from Cart** - Remove unwanted items\n"
        "💳 **Checkout** - Complete your purchase\n\n"
        "Need more help? Contact support: @yoursupport"
    )
    
    await callback.message.edit_text(help_text, reply_markup=builder.as_markup(), parse_mode='Markdown')

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery) -> None:
    """Return to main menu."""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🛍️ Browse Products", callback_data='browse_products'),
        InlineKeyboardButton(text="🛒 View Cart", callback_data='view_cart'),
        InlineKeyboardButton(text="ℹ️ Help", callback_data='help')
    )
    builder.adjust(1)
    
    await callback.message.edit_text(
        '🛒 **Welcome to our E-Store!**\n\n'
        'What would you like to do?',
        reply_markup=builder.as_markup(),
        parse_mode='Markdown'
    )

@router.callback_query(F.data == "out_of_stock")
async def out_of_stock(callback: CallbackQuery) -> None:
    """Handle out of stock callback."""
    await callback.answer("This item is currently out of stock!", show_alert=True)

async def main() -> None:
    """Start the bot."""
    # Include router in dispatcher
    dp.include_router(router)
    
    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
