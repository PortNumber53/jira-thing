# jira-thing
a Jira thing



## Run tests

```
python3 -m pytest tests/test_jira_client.py -v
```

## Configuration

### Configuration Sources

The application supports configuration from two sources:

1. `.env` file in the project directory
2. `~/.config/jira-thing/environment.conf` configuration file

#### Configuration File Format

The configuration file (`environment.conf`) uses the INI format. Example:

```ini
[jira]
JIRA_BASE_URL=https://your-jira-instance.atlassian.net
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_api_token

[gemini]
GEMINI_API_KEY=your_google_ai_api_key
GEMINI_MODEL_NAME=gemini-pro

[logging]
# Optional: Set debug level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
DEBUG_LEVEL=INFO
```

**Note**: Environment variables in `.env` take precedence over values in the configuration file.
