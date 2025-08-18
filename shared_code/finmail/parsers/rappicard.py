"""RappiCard Parser."""

from bs4 import BeautifulSoup
from dateutil import tz

from shared_code.finmail.config import settings
from shared_code.finmail.models import Transaction
from shared_code.finmail.utils.text import normalize

TZ = tz.gettz(settings.DEFAULT_TZ)

LABELS = {
    "amount": ["monto"],
    "account_last4": ["método de pago", "metodo de pago"],
    "auth_code": [
        "no. de autorización",
        "numero de autorizacion",
        "n° de autorización",
    ],
    "merchant": ["comercio", "merchant"],
    "date_local": ["fecha de la transacción", "fecha de la transaccion"],
}


def _find_value_by_label(soup: BeautifulSoup, label_variants: list[str]) -> str | None:
    for p in soup.find_all("p"):
        txt = normalize(p.get_text())
        if any(normalize(v) == txt for v in label_variants):
            tr = p.find_parent("tr")
            if not tr:
                continue
            ps = tr.find_all("p")
            if len(ps) >= 2:  # noqa: PLR2004
                return ps[1].get_text(strip=True)
    return None


class RappiCardParser:
    """Parser for RappiCard emails."""

    DOMAINS = ("rappi.nreply@rappi.com",)

    def matches(
        self,
        sender: str,
        subject: str,
        html: str | None,  # noqa: ARG002
        text: str | None,  # noqa: ARG002
    ) -> bool:
        """
        Determine if the given email matches criteria for RappiCard emails.

        Parameters
        ----------
        sender : str
            The email address of the sender.
        subject : str
            The subject line of the email.
        html : str or None
            The HTML content of the email (unused).
        text : str or None
            The plain text content of the email (unused).

        Returns
        -------
        bool
            True if the sender is in the allowed domains or if "rappicard" is present in
                the subject, False otherwise.
        """
        sender = (sender or "").lower()
        subject = (subject or "").lower()
        return (sender in self.DOMAINS) or "rappicard" in subject

    @staticmethod
    def parse(
        sender: str,  # noqa: ARG004
        subject: str,  # noqa: ARG004
        html: str | None,
        text: str | None,  # noqa: ARG004
    ) -> Transaction:
        """
        Parse a RappiCard transaction email and extracts relevant details.

        Parameters
        ----------
        sender : str
            The sender's email address. (Unused)
        subject : str
            The subject of the email, used as a fallback for description.
        html : str or None
            The HTML content of the email to parse for transaction details.
        text : str or None
            The plain text content of the email. (Unused)

        Returns
        -------
        Transaction
            A Transaction object populated with extracted details from the email.
        """
        soup = BeautifulSoup(html or "", "lxml")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        last4 = _find_value_by_label(soup, LABELS["account_last4"])
        amount = _find_value_by_label(soup, LABELS["amount"])
        date_str = _find_value_by_label(soup, LABELS["date_local"])
        merchant = _find_value_by_label(soup, LABELS["merchant"])

        amount_float = (
            (-float(amount.replace("$", "").replace(".", "").strip())) if amount else 0
        )

        description = f"Purchase at {merchant}. {settings.service_signature}."

        return Transaction(
            pocket="RappiCard",
            date_local=" ".join(date_str.split()) if date_str else None,
            amount=amount_float,
            currency="COP",
            merchant=merchant,
            account_last4=last4.replace("*", "").strip() if last4 else None,
            auth_code=_find_value_by_label(soup, LABELS["auth_code"]),
            description=description,
        )
