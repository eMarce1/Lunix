import json
import os

import discord
from discord.ext import commands
import random


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
    file_path = "./cogs/portfolios.json"

    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r") as f:
        portfolio = json.load(f)

    return portfolio

class portfolio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="portfolio")
    async def portfolio(self, ctx):
        user_id = str(ctx.author.id)
        stock_prices = await get_stocks_data()
        user_portfolios = await get_portfolio_data()

        if user_id not in user_portfolios or not user_portfolios[user_id]:
            embed = discord.Embed(
                title="Your Stocks",
                color=0x00b0f4,
                description="You currently do not own any stocks."
            )
            await ctx.reply(embed=embed)
            return

        # Create the embed for displaying stocks
        embed = discord.Embed(
            title=f"{ctx.author.name}'s Stocks",
            color=0x00b0f4
        )

        total_value = 0

        for stock, quantity in user_portfolios[user_id].items():
            if stock == 'sales':  # Skip the sales record
                continue
            if stock not in stock_prices:
                continue

            details = stock_prices[stock]
            new_price = details['new_price']
            growth = details['growth']

            # Format growth percentage with the appropriate color
            if growth > 0:
                growth_color = "green"
                growth_arrow = "📈"
            elif growth < 0:
                growth_color = "red"
                growth_arrow = "📉"
            else:
                growth_color = "white"
                growth_arrow = ""

            growth_formatted = f"{growth:.2f}%"
            stock_value = new_price * quantity
            total_value += stock_value

            embed.add_field(
                name=f"{stock} {growth_arrow}",
                value=f"Quantity: {quantity}\nCurrent Price: ${new_price:.2f}\nGrowth: {growth_formatted}\nValue: ${stock_value:.2f}",
                inline=False
            )

        embed.add_field(
            name="Total Portfolio Value",
            value=f"${total_value:.2f}",
            inline=False
        )

        await ctx.reply(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(portfolio(bot))