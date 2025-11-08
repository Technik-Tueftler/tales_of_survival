import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import src


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    src.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    yield sess
    sess.close()


def test_story_tale_relationship(session):
    # Create a Tale
    tale = src.TALE(genre_id=1)
    session.add(tale)
    session.commit()

    # Create two Stories, link to Tale and commit
    story1 = src.STORY(
        request="request",
        response="",
        tale_id=tale.id,
        story_type=src.StoryType.FICTION,
    )
    story2 = src.STORY(
        request="",
        response="response",
        tale_id=tale.id,
        story_type=src.StoryType.FICTION,
    )
    session.add_all([story1, story2])
    session.commit()

    # Fetch Tale and related Stories
    loaded_tale = session.query(src.TALE).filter_by(id=tale.id).one()
    assert len(loaded_tale.stories) == 2
    requests = {story.request for story in loaded_tale.stories}
    responses = {story.response for story in loaded_tale.stories}
    assert "request" in requests and "response" in responses

    # Fetch Story and related Tale
    loaded_story = session.query(src.STORY).filter_by(id=story1.id).one()
    assert loaded_story.tale.id == tale.id
