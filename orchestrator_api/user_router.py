from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import database, user_models, user_schemas, schemas
from auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: user_schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing = db.query(user_models.User).filter(
        (user_models.User.username == user.username) | 
        (user_models.User.email == user.email)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    db_user = user_models.User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=user_schemas.TokenResponse)
async def login(credentials: user_schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(user_models.User).filter(user_models.User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")

    user.last_login = datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    
    user_response = user_schemas.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        created_at=user.created_at,
        last_login=user.last_login
    )
    
    return user_schemas.TokenResponse(
        access_token=access_token,
        user=user_response
    )


@router.get("/me", response_model=user_schemas.UserResponse)
async def get_current_user_info(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    user = db.query(user_models.User).filter(user_models.User.username == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users", response_model=list[user_schemas.UserResponse])
async def list_users(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    admin = db.query(user_models.User).filter(user_models.User.username == current_user).first()
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(user_models.User).all()
    return users


@router.put("/users/{user_id}", response_model=user_schemas.UserResponse)
async def update_user(
    user_id: int,
    update: user_schemas.UserUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    admin = db.query(user_models.User).filter(user_models.User.username == current_user).first()
    if not admin or admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(user_models.User).filter(user_models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if update.email is not None:
        user.email = update.email
    if update.full_name is not None:
        user.full_name = update.full_name
    if update.role is not None:
        user.role = update.role
    if update.is_active is not None:
        user.is_active = update.is_active
    
    db.commit()
    db.refresh(user)
    return user
