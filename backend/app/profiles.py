from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Perfil
from app.schemas import Profile

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("", response_model=list[Profile])
def list_profiles(db: Session = Depends(get_db)):
    return db.query(Perfil).all()