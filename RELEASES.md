# Upcoming Release 1.7.0
## Major features and improvements

## Bug fixes and other changes

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
