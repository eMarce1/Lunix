from dotenv import load_dotenv
import os
import asyncio
import os

import discord
from discord.ext import commands, tasks
import json
import random
import time
from datetime import datetime, timedelta
import pytz

# APIs
load_dotenv()
discord_api = os.getenv("discord_api")


# Discord API Initialization
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

async def get_stocks_data():
    file_path = "./cogs/stocks.json"

    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r") as f:
        stock_prices = json.load(f)

    # Ensure each stock has the correct format
    for stock in stock_prices:
        if not isinstance(stock_prices[stock], dict):
            # Convert old format to new format
            stock_prices[stock] = {
                "base_price": stock_prices[stock],
                "new_price": stock_prices[stock],
                "growth": 0.0
            }

    with open(file_path, "w") as f:
        json.dump(stock_prices, f, indent=4)

    return stock_prices


async def update_stock_prices():
    with open("./cogs/stocks.json", "r") as f:
        stock_data = json.load(f)

    recent_buy_activity, recent_sell_activity = get_recent_activity()
    ny_time = datetime.now(pytz.timezone('America/New_York'))

    # Run calculations only between 4:00 and 21:30 NY time
    if ny_time.hour >= 21 or ny_time.hour < 4:
        return

    for stock, details in stock_data.items():
        base_price = details['base_price']
        current_growth = details.get('growth', 0)
        recent_buys = recent_buy_activity.get(stock, 0)
        recent_sells = recent_sell_activity.get(stock, 0)

        # Baseline chance for growth or decline
        baseline_chance = random.uniform(-0.1, 0.1)  # Allows for small positive or negative baseline growth

        # Adjust chance based on recent activities
        if recent_buys > recent_sells:
            activity_chance = 1
        elif recent_sells > recent_buys:
            activity_chance = -1
        else:
            activity_chance = 0

        # Combine baseline chance with activity-based chance
        combined_chance = baseline_chance + activity_chance * random.uniform(0.5, 1.5)

        # Apply combined chance to calculate growth rate
        growth_rate = random.uniform(0.0001, 0.001) * combined_chance
        new_growth = current_growth + growth_rate
        new_price = base_price * (1 + new_growth)

        # Ensure that new growth and new price are not excessively skewed
        if new_price < 0:
            new_price = base_price  # Avoid negative prices
        if new_growth < -0.1:
            new_growth = -0.1  # Cap growth to avoid extreme values

        # Debugging output
        print(f"Stock: {stock}, Base Price: {base_price}, Current Growth: {current_growth}, Combined Chance: {combined_chance}")
        print(f"Growth Rate: {growth_rate}, New Growth: {new_growth}, New Price: {new_price}")

        stock_data[stock]['growth'] = new_growth
        stock_data[stock]['new_price'] = new_price

    with open("./cogs/stocks.json", "w") as f:
        json.dump(stock_data, f, indent=4)

    print("Stock prices updated successfully")

def get_recent_activity():
    with open("./cogs/portfolios.json", "r") as f:
        portfolios = json.load(f)

    now = time.time()
    recent_buy_activity = {}
    recent_sell_activity = {}

    for user_id, stocks in portfolios.items():
        for stock, details in stocks.items():
            if isinstance(details, int):
                # Handle integer quantity directly
                if now - details < 5 * 3600:
                    if details > 0:
                        recent_buy_activity[stock] = recent_buy_activity.get(stock, 0) + details
                    else:
                        recent_sell_activity[stock] = recent_sell_activity.get(stock, 0) + abs(details)
            elif isinstance(details, dict):
                # Handle dictionary format with quantity and timestamp
                if 'quantity' in details and 'timestamp' in details:
                    quantity = details['quantity']
                    timestamp = details['timestamp']
                    if now - timestamp < 5 * 3600:
                        if quantity > 0:
                            recent_buy_activity[stock] = recent_buy_activity.get(stock, 0) + quantity
                        else:
                            recent_sell_activity[stock] = recent_sell_activity.get(stock, 0) + abs(quantity)
            elif isinstance(details, list):
                # Handle list of transactions
                for record in details:
                    if 'stock' in record and 'amount' in record and 'timestamp' in record:
                        if record['stock'] == stock:
                            amount = record['amount']
                            timestamp = record['timestamp']
                            if now - timestamp < 5 * 3600:
                                if amount > 0:
                                    recent_buy_activity[stock] = recent_buy_activity.get(stock, 0) + amount
                                else:
                                    recent_sell_activity[stock] = recent_sell_activity.get(stock, 0) + abs(amount)

    return recent_buy_activity, recent_sell_activity

# Function to update stock prices
async def update_stock_prices():
    stock_data = await get_stocks_data()
    recent_buy_activity, recent_sell_activity = get_recent_activity()
    ny_time = datetime.now(pytz.timezone('America/New_York'))

    # Only run calculations between 4:00 and 21:30 NY time
    if ny_time.hour >= 21 or ny_time.hour < 4:
        return

    for stock, details in stock_data.items():
        base_price = details['base_price']
        current_growth = details.get('growth', 0)
        current_price = details.get('new_price', base_price)
        recent_buys = recent_buy_activity.get(stock, 0)
        recent_sells = recent_sell_activity.get(stock, 0)

        # Determine the chance
        if recent_buys > recent_sells:
            chance = 1 if random.random() < 0.75 else 0 if random.random() < 0.25 else -1
        elif recent_sells > recent_buys:
            chance = -1 if random.random() < 0.75 else 0 if random.random() < 0.25 else 1
        else:
            chance = 0 if random.random() < 0.60 else 1 if random.random() < 0.25 else -1

        # Ensure that if growth makes the price exceed the base price, the chance is -1
        if current_price * (1 + current_growth) > base_price:
            chance = -1

        # Ensure that if the new price is less than the base price, the chance is more likely to be 1
        if current_price * (1 + current_growth) < base_price:
            chance = 1

        # Random growth value between 0.0001 and 0.001
        growth_rate = random.uniform(0.001, 0.01)
        if chance == 0:
            growth_rate = 0
        elif chance == -1:
            growth_rate = -growth_rate

        # Calculate new growth and price
        new_growth = current_growth + growth_rate
        new_price = base_price * (1 + new_growth)

        # Update stock data
        stock_data[stock]['growth'] = new_growth
        stock_data[stock]['new_price'] = new_price

    print(f"Stock: {stock}")
    print(f" - Chance: {chance}")
    print(f" - Growth: {new_growth:.6f}")
    print(f" - New Price: ${new_price:.2f}")

    # Save updated stock data
    with open("./cogs/stocks.json", "w") as f:
        json.dump(stock_data, f, indent=4)




# Starting the bot
@tasks.loop(minutes=1)
async def update_activity():
    activities = [
        discord.Activity(type=discord.ActivityType.watching, name="TheLinuxHideout"),
        discord.Activity(type=discord.ActivityType.watching, name="Youtube"),
        discord.Activity(type=discord.ActivityType.playing, name="Bedwars"),
        discord.Activity(type=discord.ActivityType.playing, name="With my balls")
    ]
    for activity in activities:

        
        await bot.change_presence(status=discord.Status.online, activity=activity)
        print("update activity ok")
        await asyncio.sleep(60)

@tasks.loop(minutes=10)
async def periodically_update_prices():
    try:
        await update_stock_prices()
    except Exception as e:
        print(f"Error in periodically_update_prices: {e}")


@tasks.loop(hours=24)
async def reset_base_prices():
    ny_time = datetime.now(pytz.timezone('America/New_York'))
    if ny_time.hour == 21 and ny_time.minute == 30:
        with open("./cogs/stocks.json", "r") as f:
            stock_data = json.load(f)

        for stock, details in stock_data.items():
            details['base_price'] = details['new_price']
            details['growth'] = 0

        with open("./cogs/stocks.json", "w") as f:
            json.dump(stock_data, f, indent=4)

    print("reset stock prices ok")



@bot.event
async def on_ready():
    files = os.listdir("./cogs")

    for filename in files:
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
    print(f"Logged in as {bot.user}")
    periodically_update_prices.start()
    reset_base_prices.start()
    await update_activity()
 

bot.run(discord_api)