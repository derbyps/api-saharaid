# Product Requirements Document — Saharaid Backoffice

## 1. Overview

Saharaid Backoffice is an internal application for managing participants, instructors, courses, schedules, and enrollments for professional training and certification programs.

The system uses:

- Amazon RDS for PostgreSQL for operational and relational data.
- Sanity as the source of truth for course content and course media.
- Amazon S3 for direct file upload, temporary storage, and document download.
- Amazon Cognito for backoffice authentication, API Gateway HTTP API for protected routes, and Python AWS Lambda functions for backend operations. One Serverless service defines the functions and routes.

Certificate management is intentionally excluded until its requirements are confirmed.

## 2. Product goals

- Give backoffice users one place to manage training operations.
- Keep large file bytes outside PostgreSQL and outside normal API payloads.
- Minimize backend API calls without returning unnecessary data.
- Keep Lambda execution time and memory use bounded, especially during course asset finalization.
- Keep Sanity credentials and all privileged database access on the backend.
- Preserve stable, monotonic participant serial numbers and yearly schedule batch numbers.

## 3. Non-goals

- Migrating all existing Sanity course data into PostgreSQL.
- Serving course lists from PostgreSQL; the frontend reads course lists from Sanity.
- Proxying file uploads or downloads through Lambda when a signed S3 URL can be used.
- Amazon RDS Proxy and a public registration endpoint.
- Certificate generation, issuance, verification, or lifecycle management.
- Defining frontend layouts or component implementation.

## 4. Data ownership

| Data | Source of truth | PostgreSQL mirror |
| --- | --- | --- |
| Course content and course assets | Sanity | `sanity_id`, title, and relational IDs required by backoffice operations |
| Course theme content and icons | Sanity | `sanity_id`, title, and slug |
| Course type, class type, and certificate-validity options | Sanity | `sanity_id` plus the labels/codes needed for PostgreSQL foreign keys |
| Participants, instructors, schedules, and enrollments | PostgreSQL | Not applicable |
| Participant and instructor file bytes | Amazon S3 | File metadata only |
| Course upload staging | Amazon S3 | Upload/finalization state only when required |

Sanity write tokens and privileged AWS credentials must never be exposed to the frontend. PostgreSQL stores S3 object keys, not permanent public URLs.

All Sanity identifiers are stored as `text`, not UUID. The course, course-theme, course-type, class-type, and certificate-validity data involved in backoffice relationships must be migrated to their PostgreSQL mirrors before the backend goes live. There is no existing production data to reconcile.

## 5. Global requirements

### 5.1 Authentication and authorization

- Backoffice users are created manually in Cognito and PostgreSQL. PostgreSQL does not store passwords or refresh tokens.
- Public registration is disabled; `/register` is deprecated.
- The frontend signs in through `POST /login`; Lambda calls Cognito through boto3. Cognito manages passwords and tokens.
- PostgreSQL stores each manually provisioned user's UUID, name, and email. Email is the current Cognito-to-database lookup key; email changes in Cognito and PostgreSQL must be coordinated.
- Each new teammate receives a temporary Cognito password through a secure channel, without an automated invitation email. The first login prompts the teammate to choose a new password before access tokens are returned.
- The frontend refreshes Cognito access tokens through the backend while the refresh token is valid; it does not call Cognito directly.
- Email delivery through Amazon SES and an in-app invitation workflow are deferred. Administrators handle account recovery manually until email delivery is configured.
- Every backoffice API operation requires a valid Cognito access token and a matching backoffice user in PostgreSQL.
- Privileged PostgreSQL, S3, and Sanity operations must run only on the backend.
- Signed upload and download URLs must be short-lived and restricted to the intended object key.
- The backend must verify that an object key belongs to the requested entity before recording or exposing it.

### 5.2 Performance and payload limits

- List responses must return only fields needed by the list screen; detail-only fields and document URLs must be omitted.
- Filtering, sorting, searching, and pagination must happen in PostgreSQL, not after loading all rows into a Lambda function.
- Every main-list screen is paginated. Backend list requests use `p` for page and `rp` for rows per page, defaulting to `p=1` and `rp=12`, and return `total`; the direct Sanity course query applies the same page defaults.
- A request for multiple file uploads must return all required signed URLs in one response.
- The frontend uploads and downloads file bytes directly to or from S3.
- Course files must be streamed from S3 to Sanity. Lambda must not load an entire file into memory.
- Document metadata must be recorded in one batch request after all direct uploads finish.
- Related rows needed by one screen should be returned by one backend request where practical, rather than through one request per row.
- Export generation must avoid loading file bytes and must include only non-document participant data.

### 5.3 Deletion and numbering

- Operational records use soft deletion unless a requirement explicitly states otherwise.
- Deleting a participant must not reuse its `serial_number`.
- Participant serial numbers increase globally from 1.
- Deleting a schedule must not reuse its batch number.
- Schedule batch numbers increase from 1 independently for each GMT+7 calendar year and reset for the next year.

### 5.4 Date and time policy

- The system business timezone is GMT+7 (`Asia/Jakarta`).
- PostgreSQL and backend date calculations use `Asia/Jakarta` by default.
- Timestamp columns use `timestamptz`; timestamp values are interpreted and presented in GMT+7 while PostgreSQL preserves the underlying instant.
- Date-only values such as date of birth and schedule dates use the PostgreSQL `date` type and have no timezone conversion.
- Today, Yesterday, rolling-period boundaries, yearly batch resets, and default timestamps are calculated in GMT+7.

## 6. Functional requirements

### 6.1 Participants

#### Participant list

The user can:

- View non-deleted participants.
- Filter by creation time using: Last Hour, Today, Yesterday, Last 7 Days, Last Month (rolling 30 days), Last 90 Days, and Last Year (rolling 365 days).
- Sort by oldest first, newest first, name A–Z, or name Z–A.
- Open participant details.

The list response must not contain all participant documents or generate signed URLs for every participant.

#### Create participant

- The backend creates the participant first and returns its UUID and serial number.
- Participant create and edit enforce case-insensitive uniqueness on trimmed active names and exact uniqueness on trimmed active phone numbers. Soft-deleted participants do not reserve either value.
- The frontend requests signed S3 upload URLs once for all selected documents.
- The frontend uploads each file directly to its signed URL.
- The frontend submits all successfully uploaded document metadata in one request.
- The current scope supports the eight optional document slots below; certificate documents are excluded until the certificate module is defined.
- A participant can be created without documents.

| Key | Label | Accepted content types | Maximum size |
| --- | --- | --- | --- |
| `passport_photo` | Passport Photo | `image/jpeg`, `image/png` | 1 MiB |
| `identity_card` | Identity Card | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB |
| `tax_number` | Tax Number | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB |
| `curiculum_vitae` | Curriculum Vitae | `application/pdf` | 1 MiB |
| `employment_certificate` | Employment Certificate | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB |
| `medical_certificate` | Medical Certificate | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB |
| `integrity_pact` | Integrity Pact | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB |
| `degree_certificate` | Degree Certificate | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB |

#### Participant detail and edit

- A detail request returns the participant and metadata for its documents.
- Download URLs are created only when the user requests a document download or when the detail screen explicitly needs them.
- The user can edit participant profile fields.
- Document additions and removals use batched metadata operations.

#### Course history

- From participant detail, the user can open all enrollments previously associated with that participant.
- The history can be searched by course name only and filtered by course theme.
- The response must contain the schedule and compact course data needed by the screen, without fetching each course separately from the backend.

#### Bulk import

- The frontend parses the spreadsheet locally.
- The frontend sends compact tabular JSON:

```json
{
  "headers": ["name", "phone_number", "email"],
  "data": [
    ["John", "081222", "john@example.com"],
    ["Jane", "081233", "jane@example.com"]
  ]
}
```

- The backend validates the header allowlist and every row.
- One bulk-import request accepts at most 200 participants.
- Imported participants do not include documents.
- Active participant names must be unique after trimming and case-insensitive comparison.
- Active participant phone numbers must be unique after trimming only.
- A name or phone number belonging only to a soft-deleted participant may be reused.
- Bulk import is atomic: if any row is invalid or conflicts with an existing or submitted name or phone number, the backend inserts nothing.
- A rejected import returns compact row-level errors without echoing the complete input.
- Serial numbers are allocated by PostgreSQL, never by the frontend.

#### Export

- The user can export participant profile data as an `.xlsx` file.
- Document metadata and file bytes are excluded.
- The export respects the active list filters and sorting.

### 6.2 Instructors

#### Instructor list

The user can:

- View non-deleted instructors.
- Filter by course theme using the globally loaded course-theme options.
- Sort by oldest first, newest first, name A–Z, or name Z–A.
- Request a document download.

The list response returns document availability and identifier/key metadata only. It must not generate signed download URLs for every row. A signed URL is created only after the user clicks download.

#### Create and edit instructor

- The user can create and edit an instructor linked to one course theme.
- An instructor supports one optional `curiculum_vitae` document in `application/pdf` format with a maximum size of 1 MiB.
- Creation follows the same direct-to-S3 flow as participant documents: create instructor, request one batch of signed URLs, upload directly, then record metadata once.

### 6.3 Courses

#### Course list and detail

- The frontend reads the course list directly from Sanity; the backend does not provide a duplicate course-list endpoint.
- The paginated Sanity query returns the course slice and exact total in one request.
- Course detail is read from Sanity for content and from the backend only when operational PostgreSQL data is required.
- PostgreSQL stores a thin mirror containing the Sanity ID, title, and relational IDs required for schedules, filtering, or integrity.

#### Create course

- The frontend sends course fields without file bytes to the backend.
- The backend validates the payload, creates the Sanity course document, and creates its PostgreSQL mirror.
- The frontend requests signed S3 upload URLs once for all gallery images and the brochure.
- The frontend uploads files directly to S3.
- The frontend calls one finalization endpoint with the staged object metadata.
- A course accepts at most six gallery images. Each image must be JPEG or PNG and no larger than 1 MiB.
- A brochure must be PDF and no larger than 1 MiB.
- The backend streams each S3 object to the Sanity asset endpoint, patches the Sanity course with the resulting asset references, and marks finalization complete.
- The backend verifies staged S3 object size and content type before sending it to Sanity.
- Successfully finalized temporary S3 objects are deleted immediately.
- A retried finalization request must not create duplicate course documents or duplicate PostgreSQL mirrors.

Supported course content follows the Sanity schema supplied for this project: title, slug, themes, course mode, duration, overview, objective, outline, requirement, gallery, related courses, brochure, and recommended audience. Sanity will also contain strong single-reference fields for course type, class type, and certificate validity.

#### Edit course

- Editing non-file fields updates Sanity and the PostgreSQL mirror in one backend operation.
- New or replacement files use the same S3 staging and finalization flow as creation.
- A replacement asset takes the place of the old Sanity asset. The old asset is removed only after the course successfully references the replacement.

### 6.4 Schedules

#### Schedule list and detail

- The user can view non-deleted schedules.
- The list can be filtered by course theme using the globally loaded course-theme options.
- The list supports oldest first, newest first, course name A–Z, and course name Z–A sorting.
- Schedule detail returns the schedule and its active participant list in one request.

#### Create and edit schedule

- A schedule references one course.
- Its batch number is assigned atomically by PostgreSQL for the GMT+7 calendar year of `start_date`.
- The user can edit schedule fields and remove enrollment membership in the same request.
- The edit payload may include `deleted_participant_ids`, an array of participant UUIDs to remove from the schedule.
- Participant removals must be applied in bulk, not with one backend request per participant. Additions use the enrollment flow.

### 6.5 Enrollments

- The user can view which participants are enrolled and which schedule/class they belong to.
- The list supports oldest first, newest first, participant name A–Z, and participant name Z–A sorting.
- The user can add multiple selected participants to one schedule in one request.
- Duplicate active enrollment of the same participant in the same schedule must be prevented by PostgreSQL.
- Enrollment data is the relationship between participant and schedule; a second overlapping model is not required.

### 6.6 Certificates

Certificate requirements are deferred. No certificate UI, API, schema, file slot, or workflow should be implemented until the business rules are confirmed.

## 7. Acceptance criteria

- No list endpoint loads all rows merely to filter or sort them in Lambda code.
- Every main-list screen is paginated, defaults to page 1 with 12 rows, and returns a total row count.
- No list endpoint signs one URL per returned row.
- One presign request supports all files selected for a single entity operation.
- File bytes travel directly between the browser and S3 except for the required S3-to-Sanity course stream.
- The S3-to-Sanity transfer does not buffer complete files in Lambda memory.
- Participant serial numbers are unique, monotonic, database-assigned, and never reused after deletion.
- Schedule batch numbers are unique and monotonic within a year and reset only for a new year.
- Participant detail includes document metadata, and schedule detail includes participants, without frontend N+1 API requests.
- Course creation is retry-safe and does not produce duplicate mirrors.
- Bulk import rejects more than 200 rows and rolls back the complete request on any row error.
- Course gallery and brochure constraints are verified against the actual staged S3 objects.
- Temporary course objects are absent from S3 after successful finalization.
- A new teammate cannot receive access tokens until the temporary-password challenge is completed and the Cognito email matches a PostgreSQL user.
- Certificate functionality remains absent until approved.
