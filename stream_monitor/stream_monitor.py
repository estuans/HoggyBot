import aiohttp
import discord
import json
import os
from .utils import checks
from discord.ext import commands

class StreamMonitor:
    """
    Track stream status
    """

    def __init__(self, bot, dataFile):
        self.bot = bot
        self.data = fileIO(dataFile, 'load')
        asyncio.ensure_future(self.start_monitor())

    async def start_monitor(self):
        self.bot.wait_until_ready()
        asyncio.ensure_future(self._poll())


    @staticmethod
    def makeRequest(data):
        url="https://api.twitch.tv/kraken/streams?community_id={}".format(data['community'])
        headers={'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': data['clientId']}
        return self.session.get(url, headers=headers)


    async def _poll(self):
        channel_id = self.data['channel']
        message_id = self.data['message']
        responseTxt = await makeRequest(self.data).text()
        channel = self.bot.get_channel(channel_id)
        message = self.bot.get_message(message_id)
        await self.bot.edit_message(message, responseTxt)
        await asyncio.sleep(600)
        asyncio.ensure_future(self._poll())


    @staticmethod
    def save_data(data):
        fileIO(dataFile, 'save', data)

    @commands.group(name="streammon", pass_context=True, no_pm=True, invoke_without_command=True)
    async def _streammon(self, ctx):
        """Stream monitor config"""
        await self.bot.send_cmd_help(ctx)

    @_streammon.command(name="community", pass_context=True, no_pm=True)
    async def _community(self, community_id, ctx):
        """Adds a community to track on twitch.tv. Must be the community _id_"""
        self.data['community'] = community_id
        save_data(self.data)
        await self.bot.say("Tracking community with id: {}".format(community_id))

    @_streammon.command(name="channel", pass_context=True, no_pm=True)
    async def _channel(self, channel: discord.Channel):
        self.data['channel'] = channel.id
        await self.bot.say("Set stream alerting channel to {}".format(channel.name))
        msg = await self.bot.send_message(channel, "Stream Alerts Enabled")
        self.data['message'] = msg.id
        save_data(self.data)

    @_streammon.command(name="clientid", no_pm=True)
    async def _setClientId(self, clientId):
        self.data['clientId'] = clientId
        save_data(self.data)
        await self.bot.say("Updated client Id")


def log(s):
    print("StreamMonitor: {}".format(s))

def setup(bot):
    if not os.path.exists('data/streammonitor'):
        log("Creating data/streammonitor folder")
        os.makedirs('data/wiki')

    f = 'data/streammonitor/data.json'
    if not fileOD(f, "check"):
        log("Creating empty data.json")
        fileIO(f, "save", {})

    bot.add_cog(StreamMonitor(bot, f))