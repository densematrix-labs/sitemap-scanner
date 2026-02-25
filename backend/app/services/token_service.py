from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple

from app.models.token import DeviceUsage, GenerationToken
from app.config import get_settings

settings = get_settings()


async def check_and_use_scan(db: AsyncSession, device_id: str) -> Tuple[bool, str, int]:
    """
    Check if device can perform a scan and consume one if possible.
    Returns: (allowed, reason, remaining_scans)
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    # First check for paid tokens
    result = await db.execute(
        select(GenerationToken)
        .where(GenerationToken.device_id == device_id)
        .where(GenerationToken.tokens_remaining > 0)
    )
    token = result.scalar_one_or_none()
    
    if token:
        token.tokens_remaining -= 1
        await db.commit()
        return True, "paid", token.tokens_remaining
    
    # Check free tier
    result = await db.execute(
        select(DeviceUsage).where(DeviceUsage.device_id == device_id)
    )
    usage = result.scalar_one_or_none()
    
    if not usage:
        # New device - create record
        usage = DeviceUsage(device_id=device_id, scans_today=1, last_scan_date=today)
        db.add(usage)
        await db.commit()
        return True, "free", settings.FREE_SCANS_PER_DAY - 1
    
    # Reset count if new day
    if usage.last_scan_date != today:
        usage.scans_today = 1
        usage.last_scan_date = today
        await db.commit()
        return True, "free", settings.FREE_SCANS_PER_DAY - 1
    
    # Check if quota exhausted
    if usage.scans_today >= settings.FREE_SCANS_PER_DAY:
        return False, "quota_exhausted", 0
    
    # Consume free scan
    usage.scans_today += 1
    await db.commit()
    return True, "free", settings.FREE_SCANS_PER_DAY - usage.scans_today


async def get_remaining_scans(db: AsyncSession, device_id: str) -> dict:
    """Get remaining scans for a device."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check paid tokens
    result = await db.execute(
        select(GenerationToken)
        .where(GenerationToken.device_id == device_id)
        .where(GenerationToken.tokens_remaining > 0)
    )
    token = result.scalar_one_or_none()
    
    paid_remaining = token.tokens_remaining if token else 0
    
    # Check free tier
    result = await db.execute(
        select(DeviceUsage).where(DeviceUsage.device_id == device_id)
    )
    usage = result.scalar_one_or_none()
    
    if not usage or usage.last_scan_date != today:
        free_remaining = settings.FREE_SCANS_PER_DAY
    else:
        free_remaining = max(0, settings.FREE_SCANS_PER_DAY - usage.scans_today)
    
    return {
        "free_remaining": free_remaining,
        "paid_remaining": paid_remaining,
        "total_remaining": free_remaining + paid_remaining
    }


async def add_tokens(db: AsyncSession, device_id: str, tokens: int, product_sku: str) -> GenerationToken:
    """Add tokens to a device account."""
    result = await db.execute(
        select(GenerationToken).where(GenerationToken.device_id == device_id)
    )
    token = result.scalar_one_or_none()
    
    if token:
        token.tokens_remaining += tokens
        token.tokens_total += tokens
        token.product_sku = product_sku
    else:
        token = GenerationToken(
            device_id=device_id,
            tokens_remaining=tokens,
            tokens_total=tokens,
            product_sku=product_sku
        )
        db.add(token)
    
    await db.commit()
    await db.refresh(token)
    return token
