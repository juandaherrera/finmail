# Finmail

Finmail is a financial email processing system built with Azure Functions. It processes transactional emails, extracts the relevant financial data, and uploads it to a Google Sheet.

## Features

- **Email Processing**: Extracts relevant financial data from incoming emails.
- **Azure Functions**: Leverages serverless architecture for scalability.
- **Google Sheets Integration**: Uploads processed data to Google Sheets for easy access and analysis.

## Getting Started
To get started with Finmail you need to have installed [UV](https://docs.astral.sh/uv/) for package management. Once you have UV installed, follow these steps:

1. Clone the repository.
2. Install dependencies using `make install`.
3. Set up local environment variables in a `.env` file.
4. Install Azure Functions Core Tools.
    * MacOS:
        ```bash
        brew tap azure/functions
        brew install azure-functions-core-tools@4
        ```
5. Start the Azure Functions host.
    ```bash
    make start
    ```

### Send Test Requests

You can use tools like `jq` or `curl` to send test requests to the Azure Functions endpoint. For example:

```bash
brew install jq
```

In this case `jq` is used to format the JSON payload for the request. You can use the following command to send a test email payload:
```bash
jq -n \
  --arg subject "RappiCard - Resumen de transacción" \
  --arg sender "rappi.nreply@rappi.com" \
  --rawfile html tests/html_samples/rappicard.html \
  '{subject:$subject, sender:$sender, html:$html}' \
| curl -sS -X POST http://localhost:7071/api/ingest \
    -H "Content-Type: application/json" \
    -d @-

```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
