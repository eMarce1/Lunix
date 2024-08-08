import os

import discord
from discord.ext import commands, tasks
import json
import random
import time
from datetime import datetime, timedelta
import pytz

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stocks(self, ctx):
        """Displays the current stock prices and their growth."""
        with open("./cogs/stocks.json", "r") as f:
            stock_data = json.load(f)

        embed = discord.Embed(title="Stock Prices", color=discord.Color.blue())

        for stock, details in stock_data.items():
            base_price = details.get('base_price', 'N/A')
            new_price = details.get('new_price', 'N/A')
            growth = details.get('growth', 0)

            # Format the growth
            if growth > 0:
                growth_color = discord.Color.green()
                growth_arrow = "📈"  # Green arrow up
            elif growth < 0:
                growth_color = discord.Color.red()
                growth_arrow = "📉"  # Red arrow down
            else:
                growth_color = discord.Color.default()
                growth_arrow = ""

            growth_percentage = f"{growth * 100:.2f}%"
            formatted_growth = f"{growth_arrow} {growth_percentage}"

            # Add stock info to the embed
            embed.add_field(
                name=f"{stock} - ${new_price:.2f}",
                value=f"Growth: {formatted_growth}",
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Stocks(bot))