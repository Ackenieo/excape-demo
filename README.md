# excape-demo

NPC_Jailbreak: A social dialogue simulator. Persuade AI gatekeepers to break rules in real-life scenarios. Designed to train your communication skills under pressure. Battle logic, share your wins or hilarious fails on Result Cards.

## Flask API Base

This repository now includes a minimal Flask API scaffold for follow-up backend development.

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
py -m venv .venv
```

2. Activate the virtual environment:

```bash
.venv\Scripts\activate
```

3. Install dependencies:

```bash
.\.venv\Scripts\python -m pip install -r requirements.txt
```

4. Optional: copy `.env.example` to `.env` and adjust values.

5. Start the API:

```bash
.\.venv\Scripts\python run.py
```

## Available Endpoints

- `GET /api/health`
- `GET /api/ping`

## Development Guidelines

### Branch Naming

Branch naming must include owner and clearly describe work:

```text
<type>-<name>-<description>
```

Examples:

- New feature: `feature-<name>-<feature description>`
- Example: `feature-jett-dev_log_system`
- Bug fix: `bugfix-<name>-<bug name>`
- Example: `bugfix-jett-login_error`
- Other types: `hotfix`, `release`

### Commit Message Convention

Commit messages must be clear and granular, with one thing per commit:

```text
<type>(<scope>): <subject>
```

Examples:

```text
feat: add new api
feat(common): add new api
```

Types:

- `feat`: new feature
- `fix`: bug fix
- `docs`: docs only
- `style`: code style, no logic change
- `build`: build or dependency changes
- `refactor`: refactoring
- `revert`: revert commit

Not used currently: `test`, `perf`, `ci`, `chore`

Subjects should not end with punctuation.

Examples:

- `feat: add new feature`
- `fix: fix a bug`

Content: remove unused imports, IDEA shortcut `Ctrl + Alt + O`.

### API Reference

#### Authentication & User (`/api/user`)

- `POST /api/user/login`: login, returns tokens
- `POST /api/user/logout`: logout with `refreshToken`, requires login
- `POST /api/user/logout-all`: logout all sessions, requires login
- `POST /api/user/refresh-token`: refresh tokens
- `POST /api/user/send-verify-code`: send SMS code
- `POST /api/user/forget`: reset password
- `POST /api/user/change-password`: change password, requires login
- `POST /api/user/change-username`: change username, requires login
- `GET /api/user/info?userId=...`: get user info, requires login

#### Chat (`/api/chat`)

Requires login unless specified otherwise.

- `POST /api/chat/consult`: AI Q&A
- `POST /api/chat/newOr`: create a new conversation ID
- `POST /api/chat/new`: archive current and start new conversation
- `GET /api/chat/history?conversationId=...`: get chat history
- `GET /api/chat/histories`: list user conversation metas
- `DELETE /api/chat/history?conversationId=...`: reset conversation history
- `GET /api/chat/secondary_question_titles/{userType}`: list common questions

#### File Review (`/api/file`)

Requires login.

- `POST /api/file/upAndwrite`: upload file and extract text with Apache Tika
- `POST /api/file/review`: review content and return structured result
- `POST /api/file/review/getId`: create a review conversation ID
- `POST /api/file/review/record?flag=...`: save review record
- `GET /api/file/review/records`: list review records
- `GET /api/file/review/record?recordId=...`: get record detail
- `DELETE /api/file/review/record?recordId=...`: delete record
- `POST /api/file/download`: download generated file

#### Knowledge Base (`/api/knowledgebs`)

Requires login.

- `GET /api/knowledgebs/query?question=...`: query by question string
- `GET /api/knowledgebs/topic`: list topics
- `GET /api/knowledgebs/case`: list common scenarios

#### MeiliSearch Debug (`/api/law/debug`)

- `GET /api/law/debug/check-index`: check `law_documents` index stats
- `GET /api/law/debug/list-indexes`: list indexes
- `POST /api/law/debug/test-add-one`: add a test document and wait for task
- `GET /api/law/debug/check-db-data`: sample DB data counts

### Authentication Header

Use `Authorization: Bearer <accessToken>` on endpoints annotated with `@LoginRequired`.

### Sample Requests

Login:

```bash
curl -X POST http://localhost:611/api/user/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"******"}'
```

Chat consult:

```bash
curl -X POST http://localhost:611/api/chat/consult \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"conversationId":"<id>","message":"...","userType":1}'
```

File extract text:

```bash
curl -X POST http://localhost:611/api/file/upAndwrite \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F file=@/path/to/contract.pdf
```

### Security & Compliance

- Never commit secrets such as `api_key`, addresses, or passwords to the repository
- Keep real sensitive configs of `application-dev.yml` and `application-prod.yml` within the team only, do not push to Git
- Avoid `git push --force` unless you fully understand the impact and have team agreement

### CI/CD

GitHub Actions is configured under `.github/workflows/` for build and deploy. Extend checks, tests, and artifact publishing as needed.

### License

Apache License 2.0, see `LICENSE`.
