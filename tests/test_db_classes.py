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

def test_create_tale_genre(session):
    """
    This test ensures that both the creation of models (tale and genre) and the one-to-one
    relationship are processed correctly by the database session. A tale can only be 
    created with an existing genre.

    Args:
        session: Pytest fixture used for a DB connection and open session.

    Asserts:
        - Assert that the retrieved object exists 
        - Assert that tales language matches "de"
        - Assert that tales relation to genre exists and the name is "Action"
    """
    genre = src.GENRE(name="Action")
    tale = src.TALE(language="de", genre=genre)
    session.add(tale)
    session.commit()

    tale_db = session.query(src.TALE).filter_by(language="de").first()
    assert tale_db is not None
    assert tale_db.language == "de"
    assert tale_db.genre.name == "Action"


def test_create_genre(session):
    """
    This test ensures that genre creation is possible without any dependencies and relationships.
    A genre can always created without any relationships.
   
    Args:
        session: Pytest fixture used for a DB connection and open session.

    Asserts:
        - Assert that the retrieved object exists 
        - Assert that genre name matches "Action"

    """
    genre = src.GENRE(name="Action")
    session.add(genre)
    session.commit()

    genre_db = session.query(src.GENRE).filter_by(name="Action").first()
    assert genre_db is not None
    assert genre_db.name == "Action"
