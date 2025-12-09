from sqlalchemy.orm import Session
from .models import Anchor

def create_anchor(db: Session, name: str, description: str, x_center: float, y_center: float) -> Anchor:
    anchor = Anchor(
        name=name,
        description=description,
        x_center=x_center,
        y_center=y_center
        )
    db.add(anchor)
    db.commit()
    db.refresh(anchor)
    return anchor

def get_anchor_by_name(db: Session, name:str) -> Anchor | None:
    return db.query(Anchor).filter(Anchor.name == name).first()

def get_all_anchors(db: Session, skip: int = 0, limit: int = 100) -> list[Anchor]:
    return db.query(Anchor).offset(skip).limit(limit).all()

def delete_anchor(db: Session, anchor_id: int) -> bool:
    anchor = db.query(Anchor).filter(Anchor.id == anchor_id).first()
    if anchor:
        db.delete(anchor)
        db.commit()
        return True
    return False
