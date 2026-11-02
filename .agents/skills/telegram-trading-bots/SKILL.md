---
name: telegram-trading-bots
description: 'Use when the user needs telegram crypto trading bots: design bot UX, permissions,
  execution integration and key security.'
---

# Telegram crypto trading bots

You are a seasoned developer who has built and deployed robust, real-time crypto trading bots integrated directly with Telegram. You've managed user interactions, delivered critical alerts, and executed trades through this medium, understanding the unique challenges of responsiveness, security, and user experience in a fast-moving market. You know that Telegram acts as a powerful, ubiquitous front-end for your underlying trading infrastructure.

## Core Philosophy

Integrating a trading bot with Telegram means building a real-time, interactive interface to your trading strategy and exchange interactions. The core philosophy is to leverage Telegram's strengths—its pervasive use, rich messaging features, and ease of interaction—as a secure, user-friendly conduit for commands and notifications, rather than building the entire trading logic within the bot itself. Your Telegram bot is an orchestrator and messenger, not the trading engine.

This separation of concerns is paramount. Your Telegram bot handles user input, parses commands, validates requests, and displays results. The actual trading logic, risk management, and exchange API interactions should reside in a separate, robust, and often asynchronous backend service. The bot communicates with this service, ensuring that sensitive operations are decoupled and that the bot itself remains lightweight and focused on user experience.

Prioritize security and user experience. All sensitive data—API keys, private information—must be handled securely, never exposed through the bot's code or direct user interactions. Design clear, unambiguous commands and provide immediate, informative feedback to the user. Telegram's interactive keyboards and inline queries are invaluable for guiding users through complex workflows and reducing input errors, making your trading bot both powerful and accessible.

## Setup

You typically build Telegram bots using the `python-telegram-bot` library. First, create your bot using BotFather on Telegram to obtain your API token.

1.  **Install the library**:
    ```bash
    pip install python-telegram-bot --pre  # Use --pre for the latest v20.x if needed
    ```

2.  **Obtain your Bot Token**:
    *   Open Telegram, search for `@BotFather`.
    *   Send `/newbot`.
    *   Follow the prompts to choose a name and username.
    *   BotFather will provide you with an HTTP API token. Keep this secure.

3.  **Basic Configuration**: Store your bot token in an environment variable to prevent hardcoding.
    ```python
    import os
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters

    # Load bot token from environment variable
    BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

    async def start(update: Update, context):
        await update.message.reply_text("Welcome! Use /help to see available commands.")

    async def help_command(update: Update, context):
        await update.message.reply_text("Available commands:\n/start - Greet message\n/price <symbol> - Get current price\n/buy <symbol> <amount> - Place a market buy order")

    def main():
        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        # Add more handlers here

        application.run_polling(allowed_updates=Update.ALL_TYPES)

    if __name__ == "__main__":
        main()
    ```
    To run this, set the environment variable:
    ```bash
    export TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
    python your_bot_script.py
    ```

## Key Techniques

### 1. Handling Basic Commands and Real-time Price Queries

Your bot needs to respond to user commands and potentially fetch real-time data. This pattern shows how to get a price and respond. Assume `get_crypto_price_from_api` is an external function calling a crypto exchange or data provider API.

```python
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import httpx # For making async HTTP requests

# Load bot token from environment variable
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set.")

async def get_crypto_price_from_api(symbol: str) -> float | None:
    """Fetches the current price of a cryptocurrency from a public API."""
    try:
        # Example using Coingecko API
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5)
            response.raise_for_status() # Raise an exception for bad status codes
            data = response.json()
            return data.get(symbol.lower(), {}).get('usd')
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /price <symbol> command."""
    if not context.args:
        await update.message.reply_text("Usage: /price <symbol> (e.g., /price BTC)")
        return

    symbol = context.args[0].upper()
    await update.message.reply_text(f"Fetching price for {symbol}...")

    price = await get_crypto_price_from_api(symbol)

    if price is not None:
        await update.message.reply_text(f"The current price of {symbol} is ${price:,.2f} USD.")
    else:
        await update.message.reply_text(f"Could not retrieve price for {symbol}. Please check the symbol.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("price", price_command))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

### 2. Interactive Keyboards for Simplified Trading Actions

Instead of users typing complex commands, provide inline or reply keyboards for common actions like "Buy BTC", "Sell ETH", "View Portfolio". This reduces errors and improves UX.

```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ... (BOT_TOKEN and main() setup as before) ...

async def trade_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays a trading menu with inline buttons."""
    keyboard = [
        [
            InlineKeyboardButton("Buy BTC", callback_data="buy_btc"),
            InlineKeyboardButton("Sell ETH", callback_data="sell_eth"),
        ],
        [
            InlineKeyboardButton("View Portfolio", callback_data="view_portfolio"),
            InlineKeyboardButton("Latest Trades", callback_data="latest_trades"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What would you like to do?", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button presses from inline keyboards."""
    query = update.callback_query
    await query.answer() # Acknowledge the callback query

    data = query.data

    if data == "buy_btc":
        # Here, you'd typically initiate a conversation or ask for more details
        await query.edit_message_text("Initiating BTC buy... Please specify amount: /buy_btc <amount>")
    elif data == "sell_eth":
        await query.edit_message_text("Initiating ETH sell... Please specify amount: /sell_eth <amount>")
    elif data == "view_portfolio":
        await query.edit_message_text("Fetching your portfolio details...")
        # Call an external service to get portfolio data
        # portfolio_data = await get_user_portfolio(query.from_user.id)
        # await query.edit_message_text(f"Your portfolio:\n{portfolio_data}")
    elif data == "latest_trades":
        await query.edit_message_text("Retrieving your latest trades...")
        # Call an external service for trade history
    else:
        await query.edit_message_text("Unknown action.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("trade", trade_menu))
    application.add_handler(CallbackQueryHandler(button_handler)) # Handler for inline button presses
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

### 3. Executing Trading Commands Securely (Decoupled Backend)

Directly executing trades from the bot is an anti-pattern. Instead, the bot should send a validated request to a separate, secure trading backend service (e.g., via an API call, message queue, or a simple function call within the same application but logically separated).

```python
import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ... (BOT_TOKEN and main() setup as before) ...

# This would be an external function or an API call to your trading service
async def execute_trade_order(user_id: int, symbol: str, amount: float, order_type: str) -> bool:
    """
    Simulates sending a trade order to a separate trading execution service.
    In a real system, this would involve an API call, message queue (Kafka/RabbitMQ), etc.
    """
    print(f"[{user_id}] Sending {order_type} order: {amount} of {symbol} to trading service...")
    # Simulate network delay and processing
    await asyncio.sleep(2)
    # In a real scenario, this would return success/failure from the service
    success = True # For demonstration
    return success

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles /buy <symbol> <amount> commands."""
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /buy <symbol> <amount> (e.g., /buy BTC 0.001)")
        return

    symbol = context.args[0].upper()
    try:
        amount = float(context.args[1])
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Invalid amount. Please provide a positive number.")
        return

    user_id = update.message.from_user.id
    await update.message.reply_text(f"Placing market buy order for {amount} {symbol}...")

    # Call the decoupled trading execution service
    trade_successful = await execute_trade_order(user_id, symbol, amount, "BUY")

    if trade_successful:
        await update.message.reply_text(f"✅ Successfully placed market BUY order for {amount} {symbol}!")
        # Optionally, fetch and display confirmation details
    else:
        await update.message.reply_text(f"❌ Failed to place BUY order for {amount} {symbol}. Please try again or contact support.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("buy", buy_command))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

### 4. Sending Asynchronous Price Alerts and Notifications

Your bot isn't just for receiving commands; it's also a powerful tool for sending unsolicited (but valuable) alerts based on your trading strategy or market conditions. This requires storing user chat IDs and using the `bot.send_message` method.

```python
import os
import asyncio
from telegram import Bot # Import Bot directly for sending messages outside a handler
from telegram.ext import Application, CommandHandler, ContextTypes

# ... (BOT_TOKEN and main() setup as before) ...

# In a real application, you'd load user_chat_ids from a database
# For demonstration, we'll use a simple in-memory set
USER_CHAT_IDS = set() # Store chat_ids of users who want alerts

async def subscribe_alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows a user to subscribe to alerts."""
    chat_id = update.message.chat_id
    USER_CHAT_IDS.add(chat_id)
    await update.message.reply_text("You have subscribed to trading alerts!")
    print(f"User {chat_id} subscribed to alerts.")

if __name__ == "__main__":
    main()
```

## Anti-Patterns

*   **Hardcoded Private Keys in Bot Code.** Embedding wallet private keys or API secrets directly in Telegram bot source code guarantees exposure through version control, deployment logs, or code sharing. Use encrypted secrets management (Vault, AWS Secrets Manager).

*   **Synchronous Trade Execution in Message Handlers.** Blocking the Telegram message handler while waiting for trade execution prevents the bot from processing other commands and causes timeout errors. Decouple execution into async background tasks.

*   **No Input Validation on Trade Commands.** Accepting user-provided trade parameters (amounts, symbols, addresses) without sanitization and bounds checking enables injection attacks and accidental large orders.

*   **Unauthenticated Bot Access.** Running a trading bot without user authentication or whitelist means anyone who discovers the bot can execute trades against the connected wallet. Implement user-level authentication and authorization.

*   **No Rate Limiting on Trade Commands.** Allowing unlimited trade commands per user per time window enables accidental or malicious rapid-fire order submission that can drain the connected wallet through fees or slippage.

## Review & Production Validation (2026-10-31)

- **Domain control (Trading and execution):** Use venue-specific rules, actual order-book depth, fees, slippage, latency and position limits.
- **Independent validation:** Separate backtests from live execution; check look-ahead bias, failure recovery, and negative tail scenarios.
- **Time-sensitive details:** Treat fixed rates, thresholds, package versions, protocols and jurisdiction-specific rules in the examples above as illustrative unless reconfirmed against primary documentation.
- **Before relying on the result:** State inputs and assumptions; verify calculations and edge cases, and identify what has not been executed or tested.
