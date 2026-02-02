<!-- # Upcoming Release 2.1.0 -->
<!-- ## Major features and improvements -->

<!-- ## Bug fixes and other changes -->

# 2.0.0
## Major features and improvements
* **Transaction Classification System**: Added automatic transaction classification based on configurable rules stored in Google Sheets.
  * Rules are loaded from a configurable worksheet (default: "ClassificationRules") with 2-column format: `conditions | category`.
  * Expression-based syntax supports single (`merchant:.*uber.*`) or multi-condition rules (`pocket:.*Rappi.* AND description:.*food.*`) with AND logic.
  * Rules evaluate in order with first-match-wins logic and case-insensitive pattern matching.
  * New `TransactionClassifier` class with lazy-loading and compiled regex patterns.
  * Classification module organized as package: `classification_rules.py`, `rule_providers.py`, and `classifier.py`.
  * Classifier initialized at module level in `core/classifier.py` for dependency injection.
  * Classification can be enabled/disabled via `ENABLE_CLASSIFICATION` setting (default: enabled).

## Bug fixes and other changes
* Added `pytest-mock` dependency for improved mocking in tests.
* Added `GOOGLE_CLASSIFICATION_WORKSHEET_NAME` setting (default: "ClassificationRules").

# 1.6.2
## Bug fixes and other changes
* Fixed validation error when `received_at` is provided as an ISO string format by changing validator mode from `before` to `after`.

# 1.6.1
## Bug fixes and other changes
* Added timezone normalization for `EmailPayload.received_at`: naive datetimes are assumed to be UTC, then all datetimes are converted to the default timezone (`America/Bogota`).

# 1.6.0
## Major features and improvements
* Added support for RemotePass payment emails (incoming funds).
* Updated `EmailPayload` and ingest pipeline to support `received_at` timestamp for accurate transaction timing when email body lacks date.

## Bug fixes and other changes
* Added `.gitattributes` file to ignore HTML files (just in the language count of GitHub) used as test fixtures.

# 1.5.0
## Major features and improvements
* Added support for "llave" (key) transfers in RappiPay, including both incoming and outgoing transactions.

## Bug fixes and other changes
* Improved description formatting for RappiPay transfers, including better handling of bank details and transaction direction.

# 1.4.0
## Major features and improvements
* Added support for PSE transactions and outgoing transfers in RappiPay parser.

## Bug fixes and other changes
* Moved `test_rappipay` fixtures to `conftest.py` for better reusability across tests.
* Removed `rappipay` keyword requirement from `RappiPay` parser to allow more flexible email subject matching.

# 1.3.0
## Major features and improvements
* Added RappiPay parser to handle transaction emails from RappiPay.
* Added date parsing utilities to handle Spanish date formats.

# 1.2.1
## Bug fixes and other changes
* Changed from `append_row` to `insert_row` in Google Sheets client to ensure new data is added at the bottom of the table instead of the bottom of the sheet.

# 1.2.0
## Major features and improvements
* Added RemotePass parser to handle transaction emails from RemotePass.

## Bug fixes and other changes
* Updated test coverage threshold from 50% to 60%.

# 1.1.1
## Bug fixes and other changes
* Added additional domain to RappiCard parser to handle emails from "noreply@rappicard.co".

# 1.1.0
## Major features and improvements
* Folder structure reorganization:
  * Moved configuration settings to `core/config.py`.
  * Moved ingest logic to `domain/ingest.py`.
  * Moved parsers to `domain/parsers/` directory.
* Added `float_from_string` utility function to handle various number formats.
  * Updated RappiCard parser to use the new `float_from_string` function for amount parsing

## Bug fixes and other changes
* Updated RappiCard parser to handle cases where the forwarded email subject is missing or cannot be normalized.

# 1.0.1
## Bug fixes and other changes
* Fixed amount parsing for RappiCard emails with decimal points in amounts.

# 1.0.0
## Major features and improvements
First release with basic functionality.
