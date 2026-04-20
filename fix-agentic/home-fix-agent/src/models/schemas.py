"""Core data models for the home fix agent."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

def _uid() -> str:
    return uuid.uuid4().hex[:12]

def _now() -> datetime:
    return datetime.now(timezone.utc)

class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class OrderStatus(str, Enum):
    PENDING = "pending_confirmation"
    CONFIRMED = "confirmed"
    PLACED = "placed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Session(BaseModel):
    session_id: str = Field(default_factory=_uid)
    created_at: datetime = Field(default_factory=_now)
    status: SessionStatus = SessionStatus.ACTIVE
    photo_path: str = ""
    description: str = ""

class IssueAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=_uid)
    session_id: str = ""
    item_category: str = ""
    problem_type: str = ""
    visible_brand: Optional[str] = None
    visible_model: Optional[str] = None
    visible_text: list[str] = Field(default_factory=list)
    description: str = ""
    confidence: float = 0.0

class ProductSpec(BaseModel):
    spec_id: str = Field(default_factory=_uid)
    session_id: str = ""
    item_category: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)
    confidence_per_field: dict[str, float] = Field(default_factory=dict)
    clarification_questions: list[str] = Field(default_factory=list)
    search_query: str = ""

class ProductResult(BaseModel):
    result_id: str = Field(default_factory=_uid)
    title: str = ""
    price_cents: int = 0
    currency: str = "USD"
    rating: float = 0.0
    review_count: int = 0
    availability: str = "in_stock"
    url: str = ""
    image_url: str = ""
    asin_or_sku: str = ""
    match_score: float = 0.0
    recommendation_reason: str = ""
    rank: int = 0

class OrderRecord(BaseModel):
    order_id: str = Field(default_factory=_uid)
    session_id: str = ""
    result_id: str = ""
    product_title: str = ""
    quantity: int = 1
    unit_price_cents: int = 0
    total_price_cents: int = 0
    shipping_cost_cents: int = 0
    retailer_order_id: str = ""
    status: OrderStatus = OrderStatus.PENDING
    confirmed_at: Optional[datetime] = None
    placed_at: Optional[datetime] = None

class PipelineResult(BaseModel):
    """Full result of a pipeline run, used for web UI state."""
    session: Session
    analysis: Optional[IssueAnalysis] = None
    spec: Optional[ProductSpec] = None
    products: list[ProductResult] = Field(default_factory=list)
    order: Optional[OrderRecord] = None
    error: Optional[str] = None
