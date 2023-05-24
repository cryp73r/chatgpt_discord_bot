import discord, openai, os
from discord import option
from dotenv import load_dotenv
from pathlib import Path
from keep_alive import keep_alive

try:
    print('On Development Environment')
    dotenv_path=Path('./dev/.env')
    load_dotenv(dotenv_path=dotenv_path)
except:
    print('On Production Environment')

bot = discord.Bot()
openai.api_key=os.getenv('OPENAI_API_KEY')
messages=[]

@bot.event
async def on_ready():
    print("Bot Ready!")

@bot.slash_command(name="ping", description="Replies with Pong followed by your Ping")
async def ping(ctx):
    latency = str(int(bot.latency * 1000))
    await ctx.respond(f'Pong :)\t{latency}ms')

@bot.slash_command(name="sync", description="Owner specific only")
async def sync(interaction: discord.Interaction):
    if (interaction.user.id==int(os.getenv('OWNER_ID'))):
        await bot.sync_commands()
        await interaction.response.send_message("Commands synced successfully")
    else:
        await interaction.response.send_message("You must be the owner to use this command!")


@bot.slash_command(name="chat", description="Chats with ChatGPT, based upon the message passed")
@option(
    "message",
    description="Enter message in similar way like you enter on web",
    required=True
)
async def chat(interaction: discord.Interaction, message: str):
    global messages
    await interaction.response.defer()
    messages.append({"role": "user", "content": message})
    if (len(messages)==100):
        messages.pop(0)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1500
        )
    response=completion.get("choices", "error")
    if (response=='error'):
        await interaction.followup.send("An error occured, please try after some time!")
        messages=[]
    else:
        outMessage=response[0]["message"]["content"]
        await interaction.followup.send(f'**Asked**: {message}')
        await interaction.followup.send(f'**Response**: {outMessage}')
        messages.append(response[0]["message"])

keep_alive()
bot.run(os.getenv('BOT_TOKEN'))