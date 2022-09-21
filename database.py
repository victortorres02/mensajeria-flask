from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker

engine = create_engine('sqlite:///database.db', echo=True)
mapper_registry = registry()
Base = mapper_registry.generate_base()
Session = sessionmaker(engine)

def init_db():
    import models
    Base.metadata.create_all(bind=engine)

