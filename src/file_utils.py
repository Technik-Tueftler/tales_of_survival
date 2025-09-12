import yaml
import aiofiles


async def load_yaml(filename):
    async with aiofiles.open(filename, mode='r', encoding="utf-8") as file:
        content = await file.read()
        data = yaml.safe_load(content)
        return data
