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
    await src.test_db(config)
    await src.test_db2(config)
    await src.test_db3(config)
    await src.test_db4(config)
    await src.test_db5(config)
    # src.openai_test(config)


if __name__ == "__main__":
    asyncio.run(main())
