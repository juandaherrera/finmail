# Upcoming Release 1.4.0
## Major features and improvements

## Bug fixes and other changes

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
