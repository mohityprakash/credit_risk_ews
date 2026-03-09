from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import AnalysisOut, ArticleOut, EntitySignalOut
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.analysis import ArticleAnalysis
from app.models.article import Article
from app.models.signal import EntitySignal
from app.services.news_pipeline import analyze_article, analyze_pending, ingest_articles

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/ingest")
def ingest(db: Session = Depends(get_db)) -> dict:
    return ingest_articles(db, get_settings())


@router.get("/articles", response_model=list[ArticleOut])
def list_articles(db: Session = Depends(get_db)):
    return db.execute(select(Article).order_by(Article.published_at.desc()).limit(500)).scalars().all()


@router.get("/articles/{article_id}")
def get_article(article_id: int, db: Session = Depends(get_db)) -> dict:
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    analysis = db.execute(select(ArticleAnalysis).where(ArticleAnalysis.article_id == article_id)).scalar_one_or_none()
    return {
        "article": ArticleOut.model_validate(article),
        "analysis": AnalysisOut.model_validate(analysis) if analysis else None,
    }


@router.get("/entities")
def list_entities(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(select(EntitySignal).order_by(EntitySignal.risk_momentum_score.desc()).limit(100)).scalars().all()
    return [EntitySignalOut.model_validate(r).model_dump() for r in rows]


@router.get("/entities/{name}/signals", response_model=list[EntitySignalOut])
def entity_signals(name: str, db: Session = Depends(get_db)):
    return db.execute(select(EntitySignal).where(EntitySignal.entity_name == name).order_by(EntitySignal.window_end.desc())).scalars().all()


@router.post("/analyze/{article_id}")
def analyze_one(article_id: int, db: Session = Depends(get_db)) -> dict:
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    if not article.is_credit_relevant:
        raise HTTPException(status_code=400, detail="Article is not credit relevant")

    existing = db.execute(select(ArticleAnalysis).where(ArticleAnalysis.article_id == article_id)).scalar_one_or_none()
    if existing:
        return {"status": "already_analyzed", "analysis_id": existing.id}

    analysis = analyze_article(db, article, get_settings())
    return {"status": "ok", "analysis_id": analysis.id}


@router.post("/analyze/pending")
def analyze_all_pending(db: Session = Depends(get_db)) -> dict:
    return analyze_pending(db, get_settings())
