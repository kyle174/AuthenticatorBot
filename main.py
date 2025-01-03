import discord
from discord.ext import commands

TOKEN = 'XYZ'

def load_approved_names(filename):
    try:
        with open(filename, 'r') as file:
            return [name.strip() for name in file.read().split(',')]
    except FileNotFoundError:
        print(f"Error: {filename} not found.")
        return []

approved_names = load_approved_names('macids.txt')

intents = discord.Intents.default()
intents.members = True  
intents.message_content = True
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_member_join(member):
    try:
        if member.dm_channel is None:
            await member.create_dm()
        attempts = 3
        verified = False
        await member.dm_channel.send(f"**WELCOME TO THE XYZ DISCORD!!!**")
      
        while attempts > 0:
            await member.dm_channel.send(f"Please reply with your **MacID** to verify your identity.")
            def check_macid(msg):
                return msg.author == member and isinstance(msg.channel, discord.DMChannel)
            try:
                macid_msg = await bot.wait_for("message", check=check_macid, timeout=300)
                if macid_msg.content.lower() in approved_names:
                    verified = True
                    await member.dm_channel.send("Your MacID has been verified! Please reply with your **full name**.")
                    break
                else:
                    attempts -= 1
                    if attempts > 0:
                        await member.dm_channel.send("Invalid MacID. Please try again.")
            except Exception as e:
                await member.dm_channel.send("You timed out due to inactivity. Please rejoin and try again.")
                return

        if not verified:
            await member.dm_channel.send("Sorry, your MacID could not be verified. Please contact a committee member for assistance.")
            return

        def check_nickname(msg):
            return msg.author == member and isinstance(msg.channel, discord.DMChannel)
        nickname_msg = await bot.wait_for("message", check=check_nickname, timeout=300)
        await member.edit(nick=nickname_msg.content)

        role = discord.utils.get(member.guild.roles, name="Verified")
        await member.add_roles(role)
        await member.dm_channel.send(f"You're all set! We are so excited to welcome you to the XYZ Discord!!!")

    except Exception as e:
        print(f"An error occurred: {e}")
        await member.dm_channel.send("You timed out due to inactivity. Please rejoin and try again.")
        return

bot.run(TOKEN)
