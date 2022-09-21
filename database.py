from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

engine = create_engine('sqlite:///database.db', echo=True)
Base = declarative_base()
Session = sessionmaker(engine)

def init_db():
    import models
    Base.metadata.create_all(bind=engine)

