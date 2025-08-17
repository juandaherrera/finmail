"""Finmail data models."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from finmail.config import settings


class Transaction(BaseModel):
    """Represents a financial transaction."""

    date_local: datetime = Field(
        description="The local date and time of the transaction",
        examples=["2023-01-01 12:00:00", "2023-01-02 13:30:00"],
    )
    pocket: str = Field(
        description="The pocket where the transaction is categorized",
        examples=["Bank X", "Bank X, pocket Y", "Cash", "Credit Card"],
    )
    category: str = Field(
        default=settings.DEFAULT_CATEGORY,
        description="The category of the transaction",
        examples=["Food", "Transport", "Utilities"],
    )
    currency: str = Field(
        description="The currency of the transaction", examples=["USD", "COP"]
    )
    amount: float = Field(
        description="The amount of the transaction", examples=[-1000.0, 2000.0]
    )
    description: str | None = Field(
        default=None, description="A description of the transaction"
    )
    notes: str | None = Field(
        default=None, description="Additional notes about the transaction"
    )

    # Additional fields
    merchant: str | None = Field(
        default=None, description="The merchant associated with the transaction"
    )
    account_last4: str | None = Field(
        default=None,
        description="The last 4 digits of the account associated with the transaction",
    )
    auth_code: str | None = Field(
        default=None, description="The authorization code for the transaction"
    )


class EmailPayload(BaseModel):
    """Represents the payload of an email to be processed."""

    subject: str = Field(description="The subject of the email")
    sender: EmailStr = Field(
        description="The sender of the email", examples=["nreply@bank.com"]
    )
    html: str | None = Field(default=None, description="The HTML content of the email")
    text: str | None = Field(
        default=None, description="The plain text content of the email"
    )
