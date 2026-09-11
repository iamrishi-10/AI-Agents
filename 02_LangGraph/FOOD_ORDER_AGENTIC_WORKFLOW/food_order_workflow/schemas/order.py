"""Pydantic schemas for order requests/responses."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class StartOrderRequest(BaseModel):
    """Schema for order start request."""
    model_config = ConfigDict(extra="forbid")
    restaurant_id: int = Field(gt=0)
    item: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class StartOrderResponse(BaseModel):
    """Schema for order start response."""
    model_config = ConfigDict(extra="forbid")
    thread_id: str
    status: str
    total_amount: float | None
    order_status: str | None
    message: str


class OrderDecisionRequest(BaseModel):
    """Schema for order decision request."""
    model_config = ConfigDict(extra="forbid")
    thread_id: str
    decision: Literal["approved", "rejected"]


class OrderDecisionResponse(BaseModel):
    """Schema for order decision response."""
    model_config = ConfigDict(extra="forbid")
    thread_id: str
    status: str
    total_amount: float | None
    order_status: str | None
    message: str
