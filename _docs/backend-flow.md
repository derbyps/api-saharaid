# Backend Flow — Saharaid Backoffice

## 1. Purpose

This document defines the new AWS backend flow. The previous Supabase implementation was unreleased and is not a migration target. `_docs/api-contract.md` defines the public HTTP contract.

The design priorities are, in order:

1. Keep credentials and privileged operations on the backend.
2. Keep file bytes out of PostgreSQL and ordinary Lambda function requests.
3. Minimize API round trips and response payloads.
4. Avoid full-file buffering and uncontrolled database connections in Lambda functions.

## 2. Request boundaries

- One Serverless service defines multiple Python Lambda functions, their API Gateway HTTP API routes, and shared configuration.
- The frontend sends a Cognito access token to API Gateway. An HTTP API JWT authorizer validates its signature, issuer, audience, and expiry before invoking a protected Lambda function.
- `POST /login` accepts credentials and invokes Cognito through boto3. If Cognito returns `NEW_PASSWORD_REQUIRED`, Lambda returns a challenge session and the frontend prompts for a new password. `POST /login/new-password` responds to the challenge through Cognito; only after it succeeds does the backend return tokens.
- `POST /login/refresh` uses the Cognito refresh token to obtain another access token. It returns a replacement refresh token when Cognito rotates it; otherwise the existing refresh token remains usable.
- The backend checks the authenticated Cognito email against a backoffice user before returning tokens. The PostgreSQL user has UUID, name, and email; Cognito owns credentials, so the table contains no password or refresh token.
- Backoffice user emails are unique under case-insensitive comparison and are provisioned with the same value as Cognito email. Never trust an email supplied in a request body for the protected-route lookup.
- The superadmin and teammates are provisioned manually in Cognito and PostgreSQL. For teammates, Cognito invitation email is suppressed and a temporary password is delivered through a secure channel. In-app invitations, SES delivery, and automated account recovery are deferred.
- Cognito self-registration is disabled. The app client permits backend password authentication; administrator-created teammate accounts use `MessageAction=SUPPRESS` and remain in `FORCE_CHANGE_PASSWORD` until the first-login challenge completes. Expired temporary passwords are reset manually by an administrator.
- On protected routes, the backend checks `token_use=access`, calls Cognito `GetUser` with the access token to obtain its email, and looks up the PostgreSQL user. The access token itself is not assumed to carry an email claim.
- For now, all provisioned backoffice users have the same access. Roles are deferred. Cognito self-service email changes must be disabled; admin email changes must be synchronized with PostgreSQL.
- Lambda functions use an IAM execution role for S3 and the required Cognito administration calls, plus backend-only configuration for PostgreSQL and Sanity credentials.
- The frontend may read public course content from Sanity, but it never receives a Sanity write token.
- The frontend uploads and downloads S3 objects using short-lived signed URLs.
- S3 stores bytes; PostgreSQL stores ownership and file metadata.
- Backoffice users are provisioned manually in Cognito and PostgreSQL. Public registration and `POST /register` are removed.

### 2.1 Database and network boundary

- Amazon RDS for PostgreSQL is accessed directly from Lambda through SQLAlchemy 2.0. There is no RDS Proxy.
- Database-backed Lambda functions run in subnets that can reach the private RDS instance. Security groups permit only the required database connection.
- Keep SQLAlchemy connection pools small and close sessions after each invocation. Lambda concurrency and database `max_connections` must be sized together.
- The same VPC-connected functions must reach Sanity and Cognito over outbound internet access and S3 through appropriate network routing or an S3 endpoint. A public subnet alone does not give VPC-connected Lambda internet access.
- Keep Sanity write tokens and database credentials in backend-only secret configuration; never send them to clients or log them.

### 2.2 PostgreSQL mirror identifiers

- Local operational tables use UUID primary keys.
- Sanity IDs use `text` columns with unique constraints; they are not assumed to be UUIDs.
- Course theme, course type, class type, and certificate-validity mirrors exist in PostgreSQL so `course` can use real foreign keys.
- The required new Sanity data is migrated to these mirror tables before backend rollout; no legacy-data reconciliation flow is needed.

### 2.3 Date and time handling

- GMT+7 (`Asia/Jakarta`) is the database and application business timezone.
- PostgreSQL timestamp columns use `timestamptz`; do not replace them with timezone-less timestamps.
- Database defaults such as `now()` and backend-generated timestamps are interpreted and returned under the GMT+7 timezone setting.
- Incoming timestamp instants are normalized by PostgreSQL and presented in GMT+7.
- `date` columns remain date-only values and are not shifted between timezones.
- Today, Yesterday, rolling filters, calendar-year boundaries, and yearly schedule batch allocation use GMT+7.

## 3. Read flows

### 3.1 List screens

```text
Frontend
  -> API Gateway HTTP API -> Lambda function: filters + sort + pagination
  -> PostgreSQL: filtered query with an explicit column selection
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
  -> PostgreSQL: schedule/enrollment/course-mirror join
  <- Lambda function -> API Gateway: compact history rows
  <- Frontend
```

This is one request per result page. It must not call Sanity once per enrollment. The PostgreSQL course mirror supplies the IDs and labels needed for filtering and rendering; the frontend can use Sanity only when opening full course content.

## 4. Participant write flows

### 4.1 Create with documents

```text
1. Frontend -> participant create
2. Backend  -> PostgreSQL inserts participant and allocates serial_number
3. Backend  -> Frontend returns participant UUID

4. Frontend -> one presign request containing all selected files
5. Backend  -> validates owner and files, returns one signed URL per file
6. Frontend -> S3 uploads directly, concurrently with a small client-side limit

7. Frontend -> one document request containing all successful upload metadata
8. Backend  -> PostgreSQL inserts document rows in one operation
```

The backend never receives the file bodies. If an upload fails, the frontend retries only that S3 upload and does not create another participant.

Participant create and update use partial unique database indexes for active rows: `lower(trim(name))` for names and `trim(phone_number)` for phone numbers. Soft-deleted rows are excluded from both indexes.

The metadata request contains the participant UUID, document type, returned S3 key, original filename, content type, size, and last-modified timestamp. Before inserting metadata, the backend performs an S3 `HEAD` request and validates object-key ownership, actual size, and actual content type.

All eight participant document types are optional and limited to 1 MiB. `passport_photo` accepts JPEG or PNG; `curiculum_vitae` accepts PDF; the other six types accept JPEG, PNG, or PDF.

### 4.2 Edit participant and documents

Profile changes use one participant update. Document changes use the same single presign request for additions and one batched metadata request containing additions and removal IDs.

For removals, ownership must be verified before deleting the S3 object and metadata row. A database failure must not silently leave metadata pointing to a deleted object.

### 4.3 Bulk import

```text
Frontend parses spreadsheet
  -> one compact { headers, data } request
Backend validates allowed headers and rows
  -> PostgreSQL transaction validates uniqueness, inserts all rows, and allocates serial numbers
Backend returns success, or compact row errors after rolling back the entire import
```

The backend rejects more than 200 rows. Active participant names are compared case-insensitively after trimming. Phone numbers are compared after trimming only. Soft-deleted rows do not reserve either value. A duplicate against active PostgreSQL rows or within the submitted batch rejects the complete import; no valid subset is inserted. The backend must not generate documents or signed URLs. The database, not `max(serial_number) + 1` in application code, owns serial allocation so concurrent imports cannot duplicate values.

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
4. Backend -> PostgreSQL: inserts thin mirror using returned sanity_id
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

Phase A must compensate if PostgreSQL mirror creation fails after Sanity creation, or leave an explicit recoverable state. Finalization must be idempotent: retrying the same course/key combination must not create another course or attach duplicate gallery entries.

Course type, class type, and certificate validity are strong single references in the updated Sanity course schema.

### 6.2 Edit course

Non-file edits require one backend request that patches Sanity and updates the PostgreSQL mirror. File additions or replacements repeat Phases B and C against the existing course. The finalization payload explicitly identifies additions, replacements, and removals; unspecified assets remain unchanged. On replacement, Sanity is patched to the new asset first and the old asset is then deleted.

### 6.3 Course reads

- List: frontend reads Sanity directly.
- Content detail: frontend reads Sanity directly.
- Operational relationships: backend reads the PostgreSQL mirror.

This avoids maintaining and transferring a second copy of rich course content.

## 7. Schedule and enrollment flows

### 7.1 Create schedule

The backend validates the course reference and dates, then performs schedule creation and yearly batch allocation atomically in PostgreSQL. Application code must not derive the next batch with an unlocked read followed by an insert.

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

The exact schedule fields remain part of the API contract, but deletions are supplied as one array and applied in bulk. Participant additions use the enrollment flow. PostgreSQL prevents duplicate active membership for the same schedule and participant.

### 7.4 Enrollment list and add

The enrollment list is a database join across enrollment, participant, schedule, and the thin course mirror, with database-side sorting and `p`/`rp` pagination. Adding participants to a schedule sends one array of participant UUIDs and performs one set-based insert.

## 8. Number allocation

### 8.1 Participant serial number

Use a PostgreSQL sequence or identity-backed counter. Sequence values are not rolled back or reused after deletion, which matches the required monotonic behavior. The frontend never submits a serial number.

### 8.2 Schedule batch number

Use a PostgreSQL-owned yearly counter allocated in the same transaction as schedule creation. The key is the GMT+7 calendar year of `start_date`, and the stored value only moves forward. Deleting a schedule does not decrement it.

## 9. Failure and retry rules

- Create entity first, then upload files; a failed upload never requires recreating the entity.
- Presign operations are safe to retry.
- Metadata writes reject keys outside the entity's S3 prefix.
- Document metadata writes verify the actual S3 object with `HEAD` before insertion.
- Batch writes return a single request result; they do not trigger frontend request loops.
- Course finalization is retry-safe and tied to one existing course identity.
- Temporary course objects are deleted from S3 immediately after successful Sanity finalization.
- S3 or Sanity failures return a stable error code and leave enough state to retry only the failed phase.
- No workflow reports success before its required database write succeeds.

## 10. Implementation status

The Lambda source files and `serverless.yml` are placeholders. This document is the target flow for the new implementation. Certificate work remains out of scope.

## AWS references

- [HTTP API JWT authorizers](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html)
- [Lambda proxy payload format 2.0](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html)
- [Direct Lambda connections to RDS](https://docs.aws.amazon.com/lambda/latest/dg/services-rds.html)
- [VPC-connected Lambda internet access](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc-internet.html)
- [Cognito administrator-created users](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-settings-admin-create-user-policy.html)
- [Cognito temporary-password challenge](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminRespondToAuthChallenge.html)
- [Cognito refresh token flows](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-the-refresh-token.html)
- [Cognito suppressed invitation email](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_AdminCreateUser.html)
- [Cognito access and ID token claims](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-with-identity-providers.html)
- [Cognito `GetUser` access token scope](https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-security-best-practices.html)
- [S3 presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
