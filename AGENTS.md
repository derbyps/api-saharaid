# Repository instructions for coding agents

Read `_docs/api-contract.md` and `_docs/backend-flow.md` for the affected feature before editing. The API contract defines HTTP fields and statuses; the backend flow defines architecture. Inspect the existing call path and adjacent feature files. Apply these conventions to new or changed code without refactoring unrelated features.

Before running AWS CLI or Serverless commands for this repository, set `export AWS_PROFILE=saharaid`. Use this profile for AWS checks and deployments.

## Feature structure

Each backend feature lives under `functions/<feature>/`:

```text
lambda_function.py          route dispatch only
handlers/GET.py             HTTP request validation and response mapping
handlers/POST.py
handlers/PUT.py
handlers/DELETE.py
services/<feature>.py       business flow and external service coordination
repositories/<feature>.py   database reads and writes
schemas/event.py            request body and query types
schemas/<feature>.py        repository Row and service Result types
schemas/response.py         HTTP Response types
```

Follow the N-layer flow: Lambda dispatches to a handler; the handler parses and validates the request, calls a service, and maps its result to a typed response; the service makes business decisions and calls repositories or shared AWS managers; repositories alone issue feature database queries. Do not put SQL, Cognito calls, or business branches in `lambda_function.py` or handlers. Keep HTTP event and response details out of services and repositories. Shared AWS operations belong in `shared/AWSManager.py`; use the existing database session and error handling utilities.

## Naming and data contracts

- Python modules, functions, methods, local variables, parameters, and internal dictionary keys use `snake_case`. Classes and schema types use `PascalCase`. Constants use `UPPER_SNAKE_CASE`.
- Repository output schemas end in `Row`; service output schemas end in `Result`; HTTP output schemas end in `Response`. Define types at the boundary where their data is produced. A handler explicitly maps a `Result` to a `Response`, even when fields look similar.
- Request schemas describe accepted JSON fields. Public JSON keys follow `_docs/api-contract.md`: `snake_case` except preserved fields such as `refreshToken`. Keep that spelling at the HTTP boundary only.
- Give methods action-oriented names such as `get_user_by_email` and `login`. Use descriptive singular names for one row and plural names for collections. Avoid generic `data`, `res`, or numbered variables where the domain name is known.
- Use `*_id` for identifiers and `*_at` for timestamps. Do not call an access token merely `id_token`; use the actual token type.
- Keep secrets, passwords, tokens, and Cognito challenge sessions out of logs and error messages. Validate request types and required values before external calls.
- Separate distinct concerns and steps with a blank line. Keep validation, database work, external calls, result mapping, and error handling visually separate; avoid dense uninterrupted blocks.

## Verification

Add one focused runnable check for nontrivial branches or security-sensitive logic. Test the public handler path and mock AWS calls; verify database lookup precedes Cognito authentication. After every code change, run Astral `ty check` on the changed Python files or feature directory and fix its diagnostics. Also run the focused test and `git diff --check`. If a broader test suite fails for an existing environment issue, report the exact blocker.
