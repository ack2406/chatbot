import os
import json
import random
import time
import requests

import tester

from discord.ext import commands
from dotenv import load_dotenv

bot = commands.Bot(command_prefix="?")

# creating list of possible responses
data_file = open('data/intents.json').read()
intents = json.loads(data_file)['intents']
tags = {x['tag']: x['responses'] for x in intents}


# enabling ai classifier
tst = tester.Tester()


# functions for responses
def get_date():
    return time.strftime("Today is %d.%m.%Y")


def get_hour():
    return time.strftime("It is %H:%M:%S")


def get_joke():
    data = requests.get("https://api.chucknorris.io/jokes/random")
    return data.json()['value']


# information about enabling discord bot
@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


# take question and responds to it
@bot.command()
async def talk(ctx, *question):
    question = " ".join(question)
    tag = tst.classify(question)
    if tag:
        if tag == "hour":
            answer = get_hour()
        elif tag == "date":
            answer = get_date()
        elif tag == "joke":
            answer = get_joke()
        else:
            answer = random.choice(tags[tag])
        await ctx.send(answer)
    else:
        await ctx.send("I'm sorry. I didn't understand. :sob:")


# listening to messages if ends with dot.
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.endswith(".") and not message.content.startswith("?"):
        response = "celnie."
        await message.channel.send(response)

    await bot.process_commands(message)


if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    bot.run(TOKEN)
