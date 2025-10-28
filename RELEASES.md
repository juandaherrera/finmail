# Upcoming Release 1.1.0
## Major features and improvements
* Folder structure reorganization:
  * Moved configuration settings to `core/config.py`.
  * Moved ingest logic to `domain/ingest.py`.
  * Moved parsers to `domain/parsers/` directory.
* Added `float_from_string` utility function to handle various number formats.
  * Updated RappiCard parser to use the new `float_from_string` function for amount parsing

## Bug fixes and other changes

# 1.0.1
## Bug fixes and other changes
* Fixed amount parsing for RappiCard emails with decimal points in amounts.

# 1.0.0
## Major features and improvements
First release with basic functionality.
