from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import Wallet, Transaction, TransactionType, User, UserRole
from app.schemas import schemas
from app.db.session import get_db
from app.core.config import settings

router = APIRouter()

@router.get("/me", response_model=schemas.Wallet)
def read_wallet_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve the current user's wallet and transaction history."""
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

@router.post("/recharge", response_model=schemas.Wallet)
def admin_recharge(
    user_id: int,
    amount: int,
    description: str = "Admin Recharge",
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Perform a wallet recharge (Admin only). Amount in cents."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Recharge amount must be positive")
    
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="User wallet not found")
    
    # Update balance
    wallet.balance += amount
    
    # Record transaction
    transaction = Transaction(
        wallet_id=wallet.user_id,
        amount=amount,
        type=TransactionType.RECHARGE,
        description=description
    )
    db.add(transaction)
    db.commit()
    db.refresh(wallet)
    return wallet

@router.post("/self-recharge", response_model=schemas.Wallet)
def self_recharge(
    amount: int,
    description: str = "Self Recharge",
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Perform a self-wallet recharge (Any authenticated user). Amount in cents."""
    if not settings.ALLOW_SELF_RECHARGE:
        raise HTTPException(status_code=403, detail="Self-recharge is currently disabled")

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Recharge amount must be positive")

    if amount > settings.MAX_SELF_RECHARGE_AMOUNT:
        max_yuan = settings.MAX_SELF_RECHARGE_AMOUNT // 100
        raise HTTPException(status_code=400, detail=f"单次充值上限为 {max_yuan} 元")

    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Update balance
    wallet.balance += amount

    # Record transaction
    transaction = Transaction(
        wallet_id=wallet.user_id,
        amount=amount,
        type=TransactionType.RECHARGE,
        description=description,
    )
    db.add(transaction)
    db.commit()
    db.refresh(wallet)
    return wallet

@router.post("/withdraw", response_model=schemas.Wallet)
def withdraw_funds(
    amount: int,
    description: str = "Withdrawal",
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Perform a wallet withdrawal (Any authenticated user). Amount in cents."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")
    
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")
    
    # Update balance
    wallet.balance -= amount
    
    # Record transaction
    transaction = Transaction(
        wallet_id=wallet.user_id,
        amount=-amount,
        type=TransactionType.WITHDRAW,
        description=description
    )
    db.add(transaction)
    db.commit()
    db.refresh(wallet)
    return wallet

@router.get("/transactions", response_model=List[schemas.Transaction])
def read_all_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """View all system transactions (Admin only)."""
    return db.query(Transaction).all()
