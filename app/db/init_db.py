from app.db.base import Base
from app.db.session import engine
from app.models.article import Article
from app.models.analysis import ArticleAnalysis
from app.models.signal import EntitySignal


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
