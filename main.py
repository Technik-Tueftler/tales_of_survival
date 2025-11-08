"""
Main function for starting application
"""
import asyncio
import src


async def main():
    """
    Scheduling function for regular call.
    """
    load_config = src.environ.to_config(src.EnvConfiguration)
    config = src.Configuration(load_config)
    await src.sync_db(config.engine)
    src.init_logging(config)
    config.logger.info(f"Start application in version: {src.__version__}")
    discord_bot = src.DiscordBot(config)
    tasks = [discord_bot.start()]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
