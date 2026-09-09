"""Pydantic schemas for refund requests/responses."""
from pydantic import BaseModel, Field, ConfigDict


class RefundRequest(BaseModel):
    """Schema for refund request."""
    model_config = ConfigDict(extra="forbid")
    order_id: int = Field(gt=0)


class RefundResponse(BaseModel):
    """Schema for refund response."""
    model_config = ConfigDict(extra="forbid")
    order_id: int
    order_status: str | None
    payment_status: str | None
    refund_eligible: bool
    refund_status: str | None


