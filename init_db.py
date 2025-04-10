
from app.models.models import Base
from app.db.database import engine

Base.metadata.create_all(bind=engine)