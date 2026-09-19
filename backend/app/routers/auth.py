from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.auth import Token, RegisterRequest, LoginRequest, PasswordChangeRequest
from app.schemas.user import UserResponse
from app.security.hashing import get_password_hash, verify_password
from app.security.jwt import create_access_token
from app.dependencies import get_current_user
from app.utils.audit_logger import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, req: Request, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    # If first user in system, automatically promote to ADMIN for initial setup ease, otherwise requested role
    user_count = db.query(User).count()
    assigned_role = UserRole.ADMIN if user_count == 0 else (request.role or UserRole.VIEWER)
    
    new_user = User(
        email=request.email.lower(),
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role=assigned_role,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    log_audit_event(
        db=db,
        user_id=new_user.id,
        action="USER_REGISTER",
        resource_type="User",
        resource_id=str(new_user.id),
        details={"email": new_user.email, "role": new_user.role.value},
        ip_address=req.client.host if req.client else None
    )
    
    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role.value})
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=new_user.role,
        email=new_user.email,
        full_name=new_user.full_name
    )

@router.post("/login", response_model=Token)
def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email.lower()).first()
    if not user or not verify_password(request.password, user.hashed_password):
        log_audit_event(
            db=db,
            user_id=None,
            action="LOGIN_FAILED",
            details={"attempted_email": request.email},
            ip_address=req.client.host if req.client else None
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
        
    log_audit_event(
        db=db,
        user_id=user.id,
        action="USER_LOGIN",
        details={"email": user.email},
        ip_address=req.client.host if req.client else None
    )
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        email=user.email,
        full_name=user.full_name
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/change-password")
def change_password(
    request: PasswordChangeRequest,
    req: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(request.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="PASSWORD_CHANGE",
        details={"user_id": current_user.id},
        ip_address=req.client.host if req.client else None
    )
    
    return {"message": "Password changed successfully"}

@router.post("/logout")
def logout(
    req: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log_audit_event(
        db=db,
        user_id=current_user.id,
        action="USER_LOGOUT",
        details={"user_id": current_user.id},
        ip_address=req.client.host if req.client else None
    )
    return {"message": "Successfully logged out"}
