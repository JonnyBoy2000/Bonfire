from .utils import config
import aiohttp
import logging
import json

log = logging.getLogger()

discord_bots_url = 'https://bots.discord.pw/api'
carbonitex_url = 'https://www.carbonitex.net/discord/data/botdata.php'


class StatsUpdate:
    """This is used purely to update stats information for carbonitex and botx.discord.pw"""

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def __unload(self):
        config.loop.create_task(self.session.close())

    async def update(self):
        
        carbon_payload = {
            'key': config.carbon_key,
            'servercount': len(self.bot.servers)
        }

        async with self.session.post(carbonitex_url, data=carbon_payload) as resp:
            log.info('Carbonitex statistics returned {} for {}'.format(resp.status, carbon_payload))
            
        payload = json.dumps({
            'server_count': len(self.bot.servers)
        })

        headers = {
            'authorization': config.discord_bots_key,
            'content-type': 'application/json'
        }

        url = '{}/bots/{}/stats'.format(discord_bots_url, self.bot.user.id)
        async with self.session.post(url, data=payload, headers=headers) as resp:
            log.info('bots.discord.pw statistics returned {} for {}'.format(resp.status, payload))

    async def on_server_join(self, server):
        await self.update()
        data = await config.get_content('bot_data')
        shard_data = data.get('shard_{}'.format(config.shard_id))
        shard_data['server_count'] = len(self.bot.servers)
        shard_data['member_count'] = len(list(self.bot.get_all_members()))
        await config.save_content('bot_data')

    async def on_server_leave(self, server):
        await self.update()
        data = await config.get_content('bot_data')
        shard_data = data.get('shard_{}'.format(config.shard_id))
        shard_data['server_count'] = len(self.bot.servers)
        shard_data['member_count'] = len(list(self.bot.get_all_members()))
        await config.save_content('bot_data')

    async def on_ready(self):
        await self.update()
        data = await config.get_content('bot_data')
        shard_data = data.get('shard_{}'.format(config.shard_id))
        shard_data['server_count'] = len(self.bot.servers)
        shard_data['member_count'] = len(list(self.bot.get_all_members()))
        await config.save_content('bot_data')


def setup(bot):
    bot.add_cog(StatsUpdate(bot))
