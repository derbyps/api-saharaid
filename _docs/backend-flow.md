# Backend Flow — Saharaid Backoffice

## 1. Purpose

This document defines the new AWS backend flow. The previous Supabase implementation was unreleased and is not a migration target. `_docs/api-contract.md` defines the public HTTP contract.

The design priorities are, in order:

1. Keep credentials and privileged operations on the backend.
2. Keep file bytes out of MySQL and ordinary Lambda function requests.
3. Minimize API round trips and response payloads.
4. Avoid full-file buffering and uncontrolled database connections in Lambda functions.

## 2. Request boundaries

- One Serverless service defines multiple Python Lambda functions, their API Gateway HTTP API routes, and shared configuration.
- Participant routes use the participant Lambda; `/files/presign-upload`, `/files/presign-download`, and `/documents` use the documents Lambda.
- The frontend sends a Cognito access token to API Gateway. An HTTP API JWT authorizer validates its signature, issuer, audience, and expiry before invoking a protected Lambda function.
- `POST /login` accepts credentials and invokes Cognito `InitiateAuth` with `USER_PASSWORD_AUTH` through boto3. If Cognito returns `NEW_PASSWORD_REQUIRED`, Lambda returns a challenge session and the frontend prompts for a new password. `POST /login/new-password` responds through Cognito `RespondToAuthChallenge`; only after it succeeds does the backend return tokens.
- `POST /login/refresh` uses the Cognito refresh token to obtain another access token. It returns a replacement refresh token when Cognito rotates it; otherwise the existing refresh token remains usable.
- The backend checks the authenticated Cognito email against a backoffice user before returning tokens. The MySQL user has UUID, name, and email; Cognito owns credentials, so the table contains no password or refresh token.
- Backoffice user emails are unique under case-insensitive comparison and are provisioned with the same value as Cognito email. Never trust an email supplied in a request body for the protected-route lookup.
- The superadmin and teammates are provisioned manually in Cognito and MySQL. For teammates, Cognito invitation email is suppressed and a temporary password is delivered through a secure channel. In-app invitations, SES delivery, and automated account recovery are deferred.
- Cognito self-registration is disabled. The app client permits backend password authentication; administrator-created teammate accounts use `MessageAction=SUPPRESS` and remain in `FORCE_CHANGE_PASSWORD` until the first-login challenge completes. Expired temporary passwords are reset manually by an administrator.
- On protected routes, the backend checks `token_use=access`, calls Cognito `GetUser` with the access token to obtain its email, and looks up the MySQL user. The access token itself is not assumed to carry an email claim.
- For now, all provisioned backoffice users have the same access. Roles are deferred. Cognito self-service email changes must be disabled; admin email changes must be synchronized with MySQL.
- Lambda functions use an IAM execution role for S3, plus backend-only configuration for MySQL and Sanity credentials.
- The frontend may read public course content from Sanity, but it never receives a Sanity write token.
- The frontend uploads and downloads S3 objects using short-lived signed URLs.
- S3 stores bytes; MySQL stores ownership and file metadata.
- Backoffice users are provisioned manually in Cognito and MySQL. Public registration and `POST /register` are removed.

### 2.1 Database and network boundary

- Amazon RDS for MySQL is accessed directly from Lambda through SQLAlchemy 2.0 and PyMySQL. There is no RDS Proxy.
- Lambda functions are not attached to a customer VPC. Each Lambda receives `RDS_HOST`, `RDS_USER`, `RDS_PASSWORD`, and `RDS_DATABASE` through the shared Serverless provider environment. `RDS_HOST` must be a publicly reachable RDS endpoint; public accessibility and database security-group ingress must be configured. Connections use TLS with certificate and hostname verification.
- Keep SQLAlchemy connection pools small and close sessions after each invocation. Lambda concurrency and database `max_connections` must be sized together.
- Lambda's default network access reaches public Cognito, S3, and Sanity endpoints.
- Keep Sanity write tokens and database credentials in backend-only secret configuration; never send them to clients or log them.

### 2.2 MySQL mirror identifiers

- Local operational tables use UUID values stored as strings.
- Sanity IDs use bounded `VARCHAR` columns with unique constraints; they are not assumed to be UUIDs.
- Course theme, course type, class type, and certificate-validity mirrors exist in MySQL so `course` can use real foreign keys.
- The required new Sanity data is migrated to these mirror tables before backend rollout; no legacy-data reconciliation flow is needed.

### 2.3 Date and time handling

- GMT+7 (`Asia/Jakarta`) is the database and application business timezone.
- MySQL connections set the session time zone to GMT+7. Defaults such as `now()` use that setting.
- `DATETIME` columns store GMT+7 business time without timezone information. Convert incoming timestamp instants to GMT+7 before storage; MySQL does not normalize `DATETIME` values.
- `date` columns remain date-only values and are not shifted between timezones.
- Today, Yesterday, rolling filters, calendar-year boundaries, and yearly schedule batch allocation use GMT+7.

### 2.4 N-layer convention

Backend features use four layers: handlers, services, repositories, and schemas. Handlers receive requests and produce API responses; services return business results; repositories return database rows; schemas define the types passed between these layers.

- Name repository output schema types with the `Row` suffix (for example, `ParticipantRow`).
- Name service output schema types with the `Result` suffix (for example, `GetParticipantsResult`).
- Name API response schema types with the `Response` suffix (for example, `PaginatedParticipantsResponse` or `ErrorResponse`). This applies to every endpoint, including error responses.
- A handler maps a service `Result` to an API `Response`; error payloads also use a `Response` type.

## 3. Read flows

### 3.1 List screens

```text
Frontend
  -> API Gateway HTTP API -> Lambda function: filters + sort + pagination
  -> MySQL: filtered query with an explicit column selection
  <- Lambda function -> API Gateway: compact rows + p + rp + total
  <- Frontend
```

Rules:

- Filter, search, sort, and paginate in the database query.
- Every backend-powered main-list request accepts `p` and `rp`, with defaults of `p=1` and `rp=12`, and returns `total`.
- Select only list columns.
- Do not attach document arrays or signed URLs.
- Join or project the small related labels needed by the screen so the frontend does not make one request per row.
- Course lists are the exception: the frontend reads a paginated slice and exact total from Sanity in one query, using the same page defaults, not from a duplicate backend endpoint.

### 3.2 Detail screens

Participant detail uses at most one backend read for profile plus document metadata. Schedule detail uses at most one backend read for schedule plus active participants. Related data should be fetched in set-based queries and assembled once, not queried inside a loop.

Signed download URLs are produced only on explicit download requests. If a screen truly needs a preview URL immediately, that screen may request it, but list endpoints must not pre-sign URLs.

### 3.3 Participant course history

```text
Frontend
  -> API Gateway HTTP API -> Lambda function: participant ID + course-name search + theme filter + p/rp
  -> MySQL: schedule/enrollment/course-mirror join
  <- Lambda function -> API Gateway: compact history rows
  <- Frontend
```

This is one request per result page. It must not call Sanity once per enrollment. The MySQL course mirror supplies the IDs and labels needed for filtering and rendering; the frontend can use Sanity only when opening full course content.

## 4. Participant write flows

### 4.1 Create with documents

```text
1. Frontend -> participant create
2. Backend  -> MySQL inserts participant and allocates serial_number
3. Backend  -> Frontend returns participant UUID

4. Frontend -> one presign request containing all selected files
5. Backend  -> validates owner ID and files, returns one signed URL per file
6. Frontend -> S3 uploads directly, concurrently with a small client-side limit

7. Frontend -> one document request containing each successful upload's document type and S3 key
8. Backend  -> inserts document rows and commits
```

The backend never receives the file bodies. If an upload fails, the frontend retries only that S3 upload and does not create another participant.

The S3 bucket CORS policy must allow the frontend origin to send direct `PUT` requests with `Content-Type`.

Participant create and update use partial unique database indexes for active rows: `lower(trim(name))` for names and `trim(phone_number)` for phone numbers. Soft-deleted rows are excluded from both indexes.

The current `POST /documents` request contains the participant owner UUID and a `files` array of document type and S3 key. The service checks that the participant exists, then writes rows with owner ID, owner type, document type, and S3 key. It does not perform an S3 `HEAD` request or validate the S3 key, content type, or file size. The ORM columns do not match the existing SQL migration's participant foreign key and file metadata columns; the metadata write has not been verified against that schema.

Presigned document keys use `docs/{owner_type}/{owner_id}/{document_type}`. `owner_type` and `document_type` must be safe path segments; presigning accepts new types without a backend owner-type allowlist.

All eight participant document types are optional and limited to 1 MiB. `passport_photo` accepts JPEG or PNG; `curiculum_vitae` accepts PDF; the other six types accept JPEG, PNG, or PDF.

### 4.2 Edit participant and documents

Profile changes use one participant update. The current document request accepts additions in `files` and removal IDs in `removed_ids`; the service applies both in one database commit.

The current removal query deletes document rows by ID without checking that they belong to the supplied owner. It does not delete S3 objects or create S3 cleanup records, so removed rows can leave objects in S3.

### 4.3 Bulk import

```text
Frontend parses spreadsheet
  -> one compact { headers, data } request
Backend validates allowed headers and rows
  -> MySQL transaction validates uniqueness, inserts all rows, and allocates serial numbers
Backend returns success, or compact row errors after rolling back the entire import
```

The backend rejects more than 200 rows. Active participant names are compared case-insensitively after trimming. Phone numbers are compared after trimming only. Soft-deleted rows do not reserve either value. A duplicate against active MySQL rows or within the submitted batch rejects the complete import; no valid subset is inserted. The backend must not generate documents or signed URLs. Bulk import must allocate consecutive serial numbers above the current maximum in one transaction and handle concurrent writes safely.

### 4.4 Export

The frontend sends the current participant filters and sorting. The backend queries only exportable participant columns and returns an `.xlsx` response. The HTTP API Lambda response carries the binary workbook using base64 encoding. No S3 reads, document joins, or signed URLs are involved.

## 5. Instructor write flows

Instructor creation and editing reuse the participant file pattern:

```text
create/update instructor
  -> one presign request for the selected document
  -> direct browser-to-S3 upload
  -> one metadata write
```

The only instructor document is optional `curiculum_vitae`, accepts PDF only, and is limited to 1 MiB.

Instructor list rows expose whether a document exists, but not a signed URL. A click on Download triggers one backend request, which verifies access and ownership and returns one short-lived signed URL; the browser then downloads directly from S3.

Participant files remain in `documents`; instructor files use `instructor_documents`. Both retain real owner foreign keys instead of a polymorphic owner column.

## 6. Course flows

### 6.1 Create course

Course creation is split into metadata creation and asset finalization so files never travel from the browser through the Lambda function.

```text
Phase A — metadata
1. Frontend -> backend: course payload without file bytes
2. Backend validates Sanity references and payload
3. Backend -> Sanity: creates course document without staged assets
4. Backend -> MySQL: inserts thin mirror using returned sanity_id
5. Backend -> frontend: course identity and upload state

Phase B — direct staging
6. Frontend -> backend: one presign request for gallery + brochure
7. Backend -> frontend: all S3 keys and signed upload URLs
8. Frontend -> S3: direct uploads

Phase C — finalization
9. Frontend -> backend: one finalize request with staged S3 keys
10. Backend -> S3: HEAD every key and verify ownership, actual type, and actual size
11. Backend -> Sanity: streams S3 response bodies to asset upload endpoints
12. Backend -> Sanity: patches the course with asset references
13. Backend: records finalization
14. Backend -> S3: deletes all finalized temporary objects
15. Backend -> frontend: returns success
```

One course accepts at most six gallery files, each JPEG or PNG and at most 1 MiB. The brochure accepts PDF only and is at most 1 MiB.

The backend streams the S3 object body into the Sanity upload request without reading the entire object into memory or converting it to base64.

Files are processed sequentially by default to keep peak Lambda memory predictable. The browser may upload directly to S3 concurrently.

Phase A must compensate if MySQL mirror creation fails after Sanity creation, or leave an explicit recoverable state. Finalization must be idempotent: retrying the same course/key combination must not create another course or attach duplicate gallery entries.

Course type, class type, and certificate validity are strong single references in the updated Sanity course schema.

### 6.2 Edit course

Non-file edits require one backend request that patches Sanity and updates the MySQL mirror. File additions or replacements repeat Phases B and C against the existing course. The finalization payload explicitly identifies additions, replacements, and removals; unspecified assets remain unchanged. On replacement, Sanity is patched to the new asset first and the old asset is then deleted.

### 6.3 Course reads

- List: frontend reads Sanity directly.
- Content detail: frontend reads Sanity directly.
- Operational relationships: backend reads the MySQL mirror.

This avoids maintaining and transferring a second copy of rich course content.

## 7. Schedule and enrollment flows

### 7.1 Create schedule

The backend validates the course reference and dates, then performs schedule creation and yearly batch allocation atomically in MySQL. Application code must not derive the next batch with an unlocked read followed by an insert.

### 7.2 Schedule detail

One request returns the schedule and its active participants. The backend uses set-based queries or a database relationship query, never one participant query per enrollment.

### 7.3 Edit schedule membership

```json
{
  "schedule": {
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  },
  "deleted_participant_ids": ["uuid-to-remove"]
}
```

The exact schedule fields remain part of the API contract, but deletions are supplied as one array and applied in bulk. Participant additions use the enrollment flow. MySQL prevents duplicate active membership for the same schedule and participant.

### 7.4 Enrollment list and add

The enrollment list is a database join across enrollment, participant, schedule, and the thin course mirror, with database-side sorting and `p`/`rp` pagination. Adding participants to a schedule sends one array of participant UUIDs and performs one set-based insert.

## 8. Number allocation

### 8.1 Participant serial number

For each create, read the maximum serial number across all participants, including soft-deleted rows, and insert the next value. Start at 1 when the table is empty. Keep the unique constraint so concurrent creates cannot store duplicate numbers; use a locked counter if concurrent writes need reliable success without a conflict retry. The frontend never submits a serial number.

### 8.2 Schedule batch number

Use a MySQL yearly counter row locked with `SELECT ... FOR UPDATE` in the same transaction as schedule creation. The key is the GMT+7 calendar year of `start_date`, and the stored value only moves forward. Deleting a schedule does not decrement it.

## 9. Failure and retry rules

- Create entity first, then upload files; a failed upload never requires recreating the entity.
- Presign operations are safe to retry.
- Document metadata writes currently do not check S3 key ownership or verify uploaded objects with `HEAD`.
- Batch writes return a single request result; they do not trigger frontend request loops.
- Course finalization is retry-safe and tied to one existing course identity.
- Temporary course objects are deleted from S3 immediately after successful Sanity finalization.
- S3 or Sanity failures return a stable error code and leave enough state to retry only the failed phase.
- No workflow reports success before its required database write succeeds.

## 10. Implementation status

`POST /login` is deployed and has been verified. `/login/new-password` and `/login/refresh` are not deployed, so first-login password changes and token refresh are not ready for frontend integration.

Participant serial assignment and the `DocumentDeletion` ORM primary key have been corrected. Participant and document routes are still not a ready frontend contract: other route and response shapes differ from §5 of the API contract, and the create → presign → S3 PUT → metadata → detail → download flow has not passed its full test.

`POST /documents` currently accepts `files` and `removed_ids` and returns `201 {}`. It stores only document type and S3 key with a polymorphic owner in the ORM, while the SQL migration requires a participant foreign key and more metadata. Removals are not owner-scoped and do not clean up S3 objects.

Certificate work remains out of scope.

The existing SQL migration files are not MySQL-compatible and need MySQL versions before applying them to a new database.

## AWS references

- [HTTP API JWT authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html)
- [Lambda proxy payload format 2.0](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html)
- [Direct Lambda connections to RDS](https://docs.aws.amazon.com/lambda/latest/dg/services-rds.html)
- [RDS public accessibility](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ModifyInstance.Settings.html)
- [Cognito administrator-created users](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-admin-create-user-policy.html)
- [Cognito temporary-password challenge](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminRespondToAuthChallenge.html)
- [Cognito refresh token flows](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-refresh-token.html)
- [Cognito suppressed invitation email](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminCreateUser.html)
- [Cognito access and ID token claims](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html)
- [Cognito `GetUser` access token scope](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-security-best-practices.html)
- [S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
