"""Tests for rule providers."""

from pytest_mock import MockerFixture

from shared_code.finmail.domain.classification import GoogleSheetsRuleProvider


def test_get_rules_success(mocker: MockerFixture) -> None:
    """Test successfully loading rules from Google Sheets."""
    mock_client = mocker.Mock()
    mock_client.read_all.return_value = [
        ["conditions", "category"],  # Header row
        ["merchant:.*uber.*", "Transport"],
        ["merchant:.*rappi.*", "Food"],
        ["description:.*transfer.*", "Transfer"],
    ]

    provider = GoogleSheetsRuleProvider(
        google_sheets_client=mock_client,
        spreadsheet_id="test-sheet-id",
        worksheet_name="ClassificationRules",
    )

    rules = provider.get_rules()

    assert len(rules) == 3
    assert rules[0].conditions == "merchant:.*uber.*"
    assert rules[0].category == "Transport"
    assert rules[1].conditions == "merchant:.*rappi.*"
    assert rules[1].category == "Food"
    assert rules[2].conditions == "description:.*transfer.*"
    assert rules[2].category == "Transfer"


def test_get_rules_multi_condition(mocker: MockerFixture) -> None:
    """Test loading multi-condition rules."""
    mock_client = mocker.Mock()
    mock_client.read_all.return_value = [
        ["conditions", "category"],  # Header row
        ["pocket:.*Rappi.* AND description:.*food.*", "Food Delivery"],
        ["pocket:.*Credit.* AND merchant:.*amazon.*", "Online Shopping"],
    ]

    provider = GoogleSheetsRuleProvider(
        google_sheets_client=mock_client,
        spreadsheet_id="test-sheet-id",
        worksheet_name="ClassificationRules",
    )

    rules = provider.get_rules()

    assert len(rules) == 2
    assert rules[0].conditions == "pocket:.*Rappi.* AND description:.*food.*"
    assert rules[0].category == "Food Delivery"
    assert rules[1].conditions == "pocket:.*Credit.* AND merchant:.*amazon.*"
    assert rules[1].category == "Online Shopping"


def test_get_rules_skips_empty_rows(mocker: MockerFixture) -> None:
    """Test that empty rows are skipped."""
    mock_client = mocker.Mock()
    mock_client.read_all.return_value = [
        ["conditions", "category"],  # Header row
        ["merchant:.*uber.*", "Transport"],
        ["", ""],  # Empty row
        ["   ", "   "],  # Whitespace only row
        [],  # Completely empty
        ["merchant:.*rappi.*", "Food"],
    ]

    provider = GoogleSheetsRuleProvider(
        google_sheets_client=mock_client,
        spreadsheet_id="test-sheet-id",
        worksheet_name="ClassificationRules",
    )

    rules = provider.get_rules()

    assert len(rules) == 2
    assert rules[0].category == "Transport"
    assert rules[1].category == "Food"


def test_get_rules_skips_insufficient_columns(mocker: MockerFixture) -> None:
    """Test that rows with less than 2 columns are skipped."""
    mock_client = mocker.Mock()
    mock_client.read_all.return_value = [
        ["conditions", "category"],  # Header row
        ["merchant:.*uber.*"],  # Missing category
        ["merchant:.*rappi.*", "Food"],  # Valid
    ]

    provider = GoogleSheetsRuleProvider(
        google_sheets_client=mock_client,
        spreadsheet_id="test-sheet-id",
        worksheet_name="ClassificationRules",
    )

    rules = provider.get_rules()

    assert len(rules) == 1
    assert rules[0].category == "Food"


def test_get_rules_skips_invalid_regex(mocker: MockerFixture) -> None:
    """Test that rows with invalid regex are skipped."""
    mock_client = mocker.Mock()
    mock_client.read_all.return_value = [
        ["conditions", "category"],  # Header row
        ["merchant:[invalid(regex", "Transport"],  # Invalid regex
        ["merchant:.*rappi.*", "Food"],  # Valid
    ]

    provider = GoogleSheetsRuleProvider(
        google_sheets_client=mock_client,
        spreadsheet_id="test-sheet-id",
        worksheet_name="ClassificationRules",
    )

    rules = provider.get_rules()

    assert len(rules) == 1
    assert rules[0].category == "Food"


def test_get_rules_handles_exception(mocker: MockerFixture) -> None:
    """Test that exceptions are handled gracefully."""
    mock_client = mocker.Mock()
    mock_client.read_all.side_effect = Exception("Connection error")

    provider = GoogleSheetsRuleProvider(
        google_sheets_client=mock_client,
        spreadsheet_id="test-sheet-id",
        worksheet_name="ClassificationRules",
    )

    rules = provider.get_rules()

    assert len(rules) == 0
