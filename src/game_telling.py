from .configuration import Configuration, ProcessInput
from .db import get_stories_messages_for_ai, update_db_objs
from .db_classes import STORY, StoryType
from .llm_handler import request_openai
from .constants import MAX_WORDS_EVENT_PROMPT

async def telling_event(config: Configuration, process_data: ProcessInput):
    commit_stories = []
    messages = await get_stories_messages_for_ai(config, process_data.story_context.tale.id)
    event_requ_prompt = (
        "Erzähl mir einen neuen Teil der Geschichte basierend auf dem folgenden Ereignis: "
        + f"{process_data.story_context.event.text} mit maximal {MAX_WORDS_EVENT_PROMPT} Wörtern."
        + "Achte darauf, dass das Ereignis so angepasst wird, dass es für ein Spieler ist, wenn nur "
        + "ein Charakter in der Geschichte ist."
    )
    messages.append({"role": "user", "content": event_requ_prompt})
    commit_stories.append(STORY(request=event_requ_prompt, story_type=StoryType.EVENT, tale_id=process_data.story_context.tale.id))
    response_event = await request_openai(config, messages)
    commit_stories.append(STORY(response=response_event, story_type=StoryType.EVENT, tale_id=process_data.story_context.tale.id))
    await update_db_objs(config, commit_stories)
