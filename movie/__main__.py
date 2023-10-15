
import os
import sys
import pandas as pd
import glob
from .server.database import Movie_base
import asyncio
import logging
import importlib
from pathlib import Path
from pyrogram import idle
from .bot import Bot
from aiohttp import web
from .server import web_server
from .bot.plug import search_ids

ppath = "movie/bot/*.py"
files = glob.glob(ppath)


loop = asyncio.get_event_loop()


async def start_services():
    print('\n')
    print('------------------- Initalizing Telegram Bot -------------------')
    await Bot.start()
    print('\n')
    print('---------------------- DONE ----------------------')
    print('\n')
    print('------------------- Importing -------------------')
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"movie/bot/{plugin_name}.py")
            import_path = ".plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["movie.bot." + plugin_name] = load
            print("Imported => " + plugin_name)
    print('\n')
    print('------------------- Initalizing Web Server -------------------')
    db=Movie_base()
    app = web.AppRunner(await web_server())
    await app.setup()
    await web.TCPSite(app, host='0.0.0.0', port=2222).start()
    print('\n')
    print('----------------------- Service Started -----------------------')
    print('                        bot =>> {}'.format((await Bot.get_me()).first_name))
    print('                        server ip =>> {}:{}'.format('http://localhost', 2222))
    print('---------------------------------------------------------------')
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        print('----------------------- Service Stopped -----------------------')
    