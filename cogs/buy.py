import os

import discord
from discord.ext import commands
import json
import time

async def get_bank_data():
    with open("./cogs/bank.json", "r") as f:
        users = json.load(f)
    return users


async def get_stocks_data():
    file_path = "./cogs/stocks.json"

    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r") as f:
        stock_prices = json.load(f)

    # Ensure each stock has the correct format
    for stock in stock_prices:
        if isinstance(stock_prices[stock], dict):
            continue
        # Handle the case where data is in the old format
        stock_prices[stock] = {
            "new_price": stock_prices[stock],
            "base_price": stock_prices[stock],
            "growth": 0.0
        }

    # Save updated format to the file if needed
    with open(file_path, "w") as f:
        json.dump(stock_prices, f, indent=4)

    return stock_prices

async def get_portfolio_data():
    try:
        with open("./cogs/portfolios.json", "r") as f:
            portfolio = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        portfolio = {}
    return portfolio

class Buy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def buy(self, ctx, stock:str, amount: int):
        stock_prices = await get_stocks_data()
        user_portfolios = await get_portfolio_data()
        users = await get_bank_data()
        user_id = str(ctx.author.id)
        stock = stock.upper()

        if stock not in stock_prices:
            embed = discord.Embed(
                title="Error",
                color=0x00b0f4,
                description=f"<@{user_id}> Stock not found!"
            )
            await ctx.reply(embed=embed)
            return

        new_price = stock_prices[stock].get("new_price", 0)
        cost = new_price * amount

        if user_id not in user_portfolios:
            user_portfolios[user_id] = {}

        if stock in user_portfolios[user_id]:
            # Ensure the portfolio entry is an integer, not a dictionary
            if isinstance(user_portfolios[user_id][stock], dict):
                user_portfolios[user_id][stock] = 0
            user_portfolios[user_id][stock] += amount
        else:
            user_portfolios[user_id][stock] = amount

        wallet = users[user_id]["wallet"]
        if cost > wallet:
            embed = discord.Embed(
                title="Error",
                color=0x00b0f4,
                description=f"<@{ctx.author.id}> You don't have enough Lunuks!"
            )
            await ctx.reply(embed=embed)
            return

        # Deduct cost from user's wallet
        users[user_id]["wallet"] -= cost

        # Add timestamp for the purchase
        timestamp = int(time.time())  # Current time in Unix timestamp format
        if 'purchases' not in user_portfolios[user_id]:
            user_portfolios[user_id]['purchases'] = []
        user_portfolios[user_id]['purchases'].append({
            "stock": stock,
            "amount": amount,
            "timestamp": timestamp
        })

        # Save updated data to JSON files
        with open("./cogs/portfolios.json", "w") as f:
            json.dump(user_portfolios, f, indent=4)
        with open("./cogs/bank.json", "w") as f:
            json.dump(users, f, indent=4)

        embed = discord.Embed(
            title="Transaction Successful!",
            color=0x00b0f4,
            description=f"<@{ctx.author.id}> You have successfully bought {amount} {stock} for {cost}!"
        )
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Buy(bot))