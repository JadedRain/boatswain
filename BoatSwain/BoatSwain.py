import dis
from pydoc import cli
import discord
import os
import json
import time
from discord.ext import commands
from discord import app_commands, reaction
import discord.interactions
from dotenv import load_dotenv as ld


ld()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

class Client(commands.Bot):
    guild = discord.Object(1126338204459610182)
    message = None
    channel = None
    emoji = None
    time_since_last_ping = time.time()

    async def on_ready(self):
        print(f'Logged on as {self.user}')
        try:
            with open('settings.json', 'r') as openfile:
                await self.load_settings(openfile)
                print("I ran correctly")
            self.tree.clear_commands(guild=None)
            synced = await self.tree.sync(guild=self.guild)
            print(f'Synced {len(synced)} commands to guild {self.guild.id}')
        except Exception as e:
            print(f'Error syncing commands: {e}')


    async def on_raw_reaction_add(self, payload):
        if (payload.member != self.user and 
                (time.time() - self.time_since_last_ping) > 10 and 
                payload.message_id == self.message and
                str(payload.emoji) == self.emoji): 

            self.time_since_last_ping = time.time()
            await self.get_channel(self.channel).send(f'<@&1195154203061002322>: {payload.member.display_name} ({payload.member.name}) wants inside the esports arena.')
            m = await self.get_channel(payload.channel_id).fetch_message(payload.message_id)
            await m.remove_reaction(self.emoji, payload.member)
            print(payload.member.display_name)

    async def load_settings(self, file):
        json_object = json.load(file)
        self.message = json_object["message"]
        self.channel = json_object["channel"]
        self.emoji = json_object["emoji"]

intents = discord.Intents.default()
intents.message_content = True

client = Client(command_prefix="!", intents=intents)


def can_run_command(interaction: discord.Interaction):
    if interaction.user.id == interaction.guild.owner_id:
        return True
    return False

@client.tree.command(name="setting", description="Settings for the bot", guild=client.guild)
@app_commands.check(can_run_command)
async def set_message(interaction: discord.Interaction, channel_id: str, message_id: str, emoji: str):
    # Code here to assign settings to client
    try:
        settings = {
            "message": int(message_id),
            "channel": int(channel_id),
            "emoji": emoji
        }

        await update_settings(client, settings)

        channel = client.get_channel(int(channel_id))
        await channel.send("This is where keyholders will be pinged when someone wants inside the arena!")
        
        msg = await interaction.channel.fetch_message(int(message_id))
        await msg.add_reaction(client.emoji)

        await interaction.response.send_message("Everything was set correctly!")
    except:
        await interaction.response.send_message("There was an issue applying settings! " + 
                                                "Make sure that both the channel and message ids are correct. " +
                                                "Also be sure to run this command in the same channel as the message you are trying to set")

async def update_settings(client, settings):
    # Save object to file
    json_object = json.dumps(settings, indent=4)

    with open("settings.json", "w") as outfile:
        outfile.write(json_object)

    # Update client
    client.message = settings["message"]
    client.channel = settings["channel"]
    client.emoji = settings["emoji"]

 
client.run(DISCORD_TOKEN)