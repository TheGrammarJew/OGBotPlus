#!/usr/bin/env python3

import logging.handlers
import os
import sys

import hikari
import pyfiglet
# import aiofiles
import toml

from OGBotPlus import OGBotPlus
from plugins.santa import Santa
from plugins.warframe import Warframe
from plugins.game import Game


if os.name != "nt":
    import uvloop

    uvloop.install()

# Logging setup

fmt = logging.Formatter('%(asctime)s - %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

log = logging.getLogger()
sh = logging.StreamHandler(sys.stderr)
sh.setFormatter(fmt)
sh.setLevel(logging.INFO)
log.addHandler(sh)

discord_logger = logging.getLogger('hikari')
discord_logger.setLevel(logging.WARNING)
discord_logger.addHandler(sh)

log_path = os.path.join("logs", "ogbot.log")
if not os.path.exists(log_path):
    os.makedirs("logs", exist_ok=True)
    with open(log_path, "x") as f:
        pass

fh = logging.handlers.TimedRotatingFileHandler(filename=log_path, when="midnight", encoding='utf-8')
fh.setFormatter(fmt)
discord_logger.addHandler(fh)
log.addHandler(fh)

log = logging.getLogger()


def load_config() -> dict:
    default = {"credentials": {'token': '', 'client_id': ''},
               "bot_configuration": {'main_guilds': [0],
                                     'tracked_guild_ids': [],
                                     'chat_channels': [0],
                                     'default_rcon_password': '',
                                     'santa_channel': 0,
                                     'local_ip': '127.0.0.1'}
               }

    try:
        with open('config.toml') as cfg:
            dd_config = toml.load(cfg)
            for k1, v1 in default.items():
                if k1 not in dd_config.keys():
                    dd_config[k1] = v1
                if isinstance(v1, dict):
                    for k2, v2 in v1.items():
                        if k2 not in dd_config[k1].keys():
                            dd_config[k1][k2] = v2

        with open('config.toml', 'w') as cfg:
            toml.dump(dd_config, cfg)
        return dd_config
    except FileNotFoundError:
        log.warning('File "config.toml" not found; Generating...')
        with open('config.toml', 'w+') as cfg:
            toml.dump(default, cfg)
        print('File "config.toml" not found; Generating...')
        print('Please input any relevant information and restart.')
        return {}


config = load_config()

# bot = lightbulb.Bot(token=config['credentials']['token'], intents=hikari.Intents.ALL, slash_commands_only=True)
bot = OGBotPlus(config=config['bot_configuration'],
                token=config['credentials']['token'],
                intents=hikari.Intents.ALL,
                prefix='>',
                owner_ids=(141752316188426241,)
                )


@bot.listen(hikari.ShardReadyEvent)
async def on_ready(event: hikari.ShardReadyEvent):
    bot_user = bot.get_me()
    print(f"""~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
{pyfiglet.figlet_format(bot_user.username, font='epic')}
Username: {bot_user.username}  |  ID: {bot_user.id}

Chat Channel: {bot.chat_channels}  |  Meme Channel: {bot.santa_channel}
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~""")


plugins = [
    Warframe,
    Santa,
    Game
]

for plugin in plugins:
    bot.add_plugin(plugin(bot))
bot.run()
