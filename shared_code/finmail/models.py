"""Finmail data models."""

from datetime import UTC, datetime

from bs4 import BeautifulSoup
from dateutil import tz
from pydantic import BaseModel, EmailStr, Field, field_validator

from shared_code.finmail.core.config import settings
from shared_code.finmail.utils.html import clean_html


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
    received_at: datetime | None = Field(
        default=None, description="The timestamp when the email was received"
    )

    @field_validator("received_at", mode="before")
    @classmethod
    def normalize_received_at_timezone(cls, value: datetime | None) -> datetime | None:
        """
        Normalize received_at to default timezone.

        If received_at has no timezone info, assume UTC.
        Then convert to the default timezone.

        Parameters
        ----------
        value : datetime | None
            The received_at datetime value to normalize.

        Returns
        -------
        datetime | None
            The normalized received_at datetime value.
        """
        if value is None:
            return None

        # If naive (no timezone), assume UTC
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)

        # Convert to default timezone
        default_tz = tz.gettz(settings.DEFAULT_TZ)
        return value.astimezone(default_tz)

    # TODO @juandaherrera: define if this should be here
    def get_soup(self) -> BeautifulSoup:
        """
        Return a cleaned HTML representation of the object's HTML content.

        This computed property uses BeautifulSoup to parse the HTML stored in the
        `html` attribute, then applies the `clean_html` function to sanitize the
        parsed content. If the `html` attribute is None or empty, an empty string
        is parsed and cleaned.

        Returns
        -------
        BeautifulSoup
            The cleaned HTML content as a string.
        """
        soup = BeautifulSoup(self.html or "", "lxml")
        clean_html(soup=soup)
        return soup
