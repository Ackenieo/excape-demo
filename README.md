# excape-demo

NPC_Jailbreak: A social dialogue simulator. Persuade AI gatekeepers to break rules in real-life scenarios. Designed to train your communication skills under pressure. Battle logic, share your wins or hilarious fails on Result Cards.

## Flask API Base

This repository includes a minimal Flask API scaffold for backend development.

## Project Structure

```text
.
|-- app/
|   |-- __init__.py
|   `-- api/
|       |-- __init__.py
|       `-- routes.py
|-- config.py
|-- requirements.txt
`-- run.py
```

## Quick Start

1. Create a virtual environment:

```bash
python -m venv .venv
```

2. Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Optional: copy `.env.example` to `.env` and adjust values.

5. Start the API:

```bash
python run.py
```

## Available Endpoints

The API currently provides the following basic endpoints (default port `5000`):

- `GET /api/health` - Health check
- `GET /api/ping` - Returns `{"message": "pong"}`
- `GET /api/get_miao` - Returns `{"message": "miao"}`

## Profile API Notes

- `GET /api/v1/profile` returns a stable personal-center payload for frontend integration.
- `rankText` now uses the player's accumulated completed-run score for global ranking and returns text like `全球第 N 名`.
- `achievements` now returns a stable list with runtime-computed `active` states.
- `avatarUrl` now points to a backend-managed image content endpoint backed by PostgreSQL image storage.
- `POST /api/v1/profile/avatar` now supports two JSON modes:
  - select default avatar: `deviceId + defaultImageId`
  - upload custom avatar: `deviceId + imageBase64 + mimeType`
- `POST /api/v1/profile/nickname` validates trimmed nickname input, requires 2 to 16 characters, and rejects placeholder values such as `null` or `游客`.
- Default avatars and custom avatars are both stored in PostgreSQL instead of external image URLs.

### Sample Requests

```bash
curl http://localhost:5000/api/health
curl http://localhost:5000/api/ping
curl http://localhost:5000/api/get_miao
```

## Development Guidelines

### Branch Naming

Branch naming must include owner and clearly describe work:

```text
<type>-<name>-<description>
```

Examples:
- New feature: `feature-<name>-<feature description>` (e.g., `feature-jett-dev_log_system`)
- Bug fix: `bugfix-<name>-<bug name>` (e.g., `bugfix-jett-login_error`)
- Other types: `hotfix`, `release`

### Commit Message Convention

Commit messages must be clear and granular, with one thing per commit:

```text
<type>(<scope>): <subject>
```

Types:
- `feat`: new feature
- `fix`: bug fix
- `docs`: docs only
- `style`: code style, no logic change
- `build`: build or dependency changes
- `refactor`: refactoring
- `revert`: revert commit

Examples:
- `feat: add new api`
- `fix(auth): resolve login error`

### Security & Compliance

- Never commit secrets such as `api_key`, addresses, or passwords to the repository
- Keep real sensitive configs out of Git
- Avoid `git push --force` unless you fully understand the impact and have team agreement

### License

Apache License 2.0, see `LICENSE`.
