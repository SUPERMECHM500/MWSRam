
# Lib
from os import popen
from asyncio import sleep
from datetime import datetime

# Site
from discord.activity import Activity
from discord.enums import ActivityType, Status
from discord.ext.commands.cog import Cog
from discord.ext.tasks import loop

# Local
from utils.classes import Bot


class BackgroundTasks(Cog):
    """Background loops"""

    def __init__(self, bot: Bot):
        self.bot = bot
        self.save_data.start()
        self.status_change.start()

    @loop(seconds=60)
    async def status_change(self):
        if self.bot.tz != "UTC":
            time = datetime.now().strftime("%H:%M")
        else:
            time = datetime.utcnow().strftime("%H:%M")

        if self.bot.Inactive >= 5:
            status = Status.idle
        else:
            status = Status.online

        if self.bot.debug_mode:
            activity = Activity(type=ActivityType.playing, name="in DEBUG MODE")
        # elif self.bot.DisableSaving:
        #     activity = Activity(type=ActivityType.playing, name=f"with SAVING DISABLED")

        else:
            activity = Activity(
                type=ActivityType.watching,
                name=f"{self.bot.command_prefix}help | {self.bot.tz}: {time}"
            )

        await self.bot.change_presence(status=status, activity=activity)

    @loop(seconds=60)
    async def save_data(self):
        time = datetime.now().strftime("%H:%M, %m/%d/%Y")

        # if not (exists(join(getcwd(), "Serialized", "data.pkl")) and
        #         exists(join(getcwd(), "Serialized", "bot_config.pkl"))) and \
        #         not self.bot.DisableSaving:
        #
        #     self.bot.DisableSaving = True
        #     print(
        #         f"[{time} || Unable to save] data.pkl and/or bot_config.pkl not found. Replace file before "
        #         f"shutting down. Saving disabled.")
        #
        #     return
        #
        # elif (exists(join(getcwd(), "Serialized", "data.pkl")) and
        #       exists(join(getcwd(), "Serialized", "bot_config.pkl"))) and \
        #         self.bot.DisableSaving:
        #
        #     self.bot.DisableSaving = False
        #     print(f"[{time}] Saving re-enabled.")
        #     return

        # if not self.bot.DisableSaving:

        await self.bot.user_data.save()

        # with open(join(getcwd(), "Serialized", "data.pkl"), "wb") as f:
        #     data = {
        #         "VanityAvatars": self.bot.VanityAvatars,
        #         "Blacklists": self.bot.Blacklists,
        #         "Closets": self.bot.Closets,
        #         "ServerBlacklists": self.bot.ServerBlacklists
        #     }
        #
        #     try:
        #         dump(data, f)
        #     except Exception as e:
        #         print(f"[{time} || Unable to save] Pickle dumping Error:", e)

        # with open(join(getcwd(), "Serialized", "bot_config.pkl"), "wb") as f:
        #     config_data = {
        #         "debug_mode": self.bot.debug_mode,
        #         "auto_pull": self.bot.auto_pull,
        #         "tz": self.bot.tz,
        #         "prefix": self.bot.command_prefix
        #     }
        #
        #     try:
        #         dump(config_data, f)
        #     except Exception as e:
        #         print("[Unknown Error] Pickle dumping error:", e)

        self.bot.Inactive = self.bot.Inactive + 1
        print(f"[VPP: {time}] Saved data.", end="\n" if not self.bot.auto_pull else "\r")

        if self.bot.auto_pull:
            print(f"[VPP: {time}] Saved data. Checking git repository for changes...{' '*30}", end="\r")
            resp = popen("git pull").read()
            resp = f"```diff\n{resp}\n```"
            if str(resp) != f"```diff\nAlready up to date.\n\n```":
                for i in self.bot.owner_ids:
                    owner = self.bot.get_user(i)
                    await owner.send(f"**__Auto-pulled from github repository and restarted cogs.__**\n{resp}")
                    print(f"[VPP: {time}] Saved data. Changes sent to owner via Discord.")

                modules = {module.__module__: cog for cog, module in self.bot.cogs.items()}
                for module in modules.keys():
                    self.bot.reload_extension(module)
            else:
                print(f'[VPP: {time}] Saved data. No new changes.{" "*30}')

    @status_change.before_loop
    async def sc_wait(self):
        await self.bot.wait_until_ready()
        await sleep(30)

    @save_data.before_loop
    async def sd_wait(self):
        await self.bot.wait_until_ready()
        await sleep(15)


def setup(bot: Bot):
    bot.add_cog(BackgroundTasks(bot))
