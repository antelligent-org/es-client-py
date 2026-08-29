# Everyday Series Python Client

A Python client for [Everyday Series](https://everydayseries.com) — token
generation and file upload.

Use it inside a **Python Run** node to write results back into your workspace,
or standalone from any script.

## Installation

```bash
pip install git+https://github.com/antelligent-org/es-client-py.git
```

Pin to a commit for anything that runs unattended, so the code that runs today
is the code that ran yesterday:

```bash
pip install git+https://github.com/antelligent-org/es-client-py.git@<commit-sha>
```

## Usage

```python
from es_client import CodeFastClient as EverydaySeriesClient

client = EverydaySeriesClient(
    email="your_email@example.com",
    team_slug="your_team_slug",
    api_key="your_api_key",
)

# Get token
client._get_token()

# Upload a file from disk
client.upload_file(file_path="path/to/your/file.txt", file_name="file.txt", file_content=None)

# Upload from bytes
client.upload_file(file_path=None, file_name="file.txt", file_content=b"This is a test file.")

# Upload from a string
client.upload_file(file_path=None, file_name="file.txt", file_content="This is a test file.")
```

> **Note on the class name.** The exported class is still `CodeFastClient`, the
> original name from before the product became Everyday Series. Importing it
> under an alias, as above, keeps the old name out of your code. A future
> release will export `EverydaySeriesClient` directly and keep `CodeFastClient`
> as a backwards-compatible alias.

## Inside a Python Run node

Select an ES API Key in the node's **Settings** tab and the node builds `client`
for you — already authenticated, already scoped to your team. Three environment
variables are provided:

| Variable | Meaning |
|---|---|
| `ES_API_KEY` | your Everyday Series API key |
| `ES_EMAIL` | the account the key belongs to |
| `ES_TEAM_SLUG` | the team the node runs in |

```python
client = EverydaySeriesClient(
    email=os.environ["ES_EMAIL"],
    team_slug=os.environ["ES_TEAM_SLUG"],
    api_key=os.environ["ES_API_KEY"],
)
```

**Never paste an API key into node code.** Node code is stored as written, so a
credential there travels with every copy, export and share of that Series. Put
secrets in **Settings → environment variables**, where they are encrypted per
team.
