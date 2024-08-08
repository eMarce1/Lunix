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
    with open("./cogs/stocks.json", "r") as f:
        stock_prices = json.load(f)
    return stock_prices


async def get_portfolio_data():
    file_path = "./cogs/portfolios.json"

    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r") as f:
        portfolio = json.load(f)

    return portfolio


class Sell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def sell(self, ctx, stock: str, amount: int):
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

        if user_id not in user_portfolios or stock not in user_portfolios[user_id] or user_portfolios[user_id][
            stock] < amount:
            embed = discord.Embed(
                title="Error",
                color=0x00b0f4,
                description=f"<@{ctx.author.id}> You do not have enough of {stock} to sell!"
            )
            await ctx.reply(embed=embed)
            return

        # Deduct amount from portfolio
        user_portfolios[user_id][stock] -= amount
        if user_portfolios[user_id][stock] == 0:
            del user_portfolios[user_id][stock]

        # Add proceeds to wallet
        if user_id not in users:
            users[user_id] = {"wallet": 0}
        users[user_id]["wallet"] += cost

        # Add timestamp for the sale
        timestamp = int(time.time())  # Current time in Unix timestamp format
        if 'sales' not in user_portfolios[user_id]:
            user_portfolios[user_id]['sales'] = []
        user_portfolios[user_id]['sales'].append({
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
            description=f"<@{ctx.author.id}> You have successfully sold {amount} {stock} for {cost}!"
        )
        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Sell(bot))