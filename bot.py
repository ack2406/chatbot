import os

from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix="?")

questions = {
    "how old are you?": "Not even a month.",
    "what are you?": "I'm a bot.",
    "tell me a yoke": """Helvetica and Times New Roman walk into a bar.
    “Get out of here!” shouts the bartender. “We don’t serve your type.”"""
}


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.command()
async def moyai(ctx):
    await ctx.send(":moyai:")


@bot.command()
async def ask(ctx, *question):
    question = " ".join(question)
    print(question, questions.keys())
    if question in questions.keys():
        await ctx.send(questions[question])
    else:
        await ctx.send("I'm sorry. I didn't understand. :sob:")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.endswith("."):
        response = "celnie."
        await message.channel.send(response)

    await bot.process_commands(message)


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
