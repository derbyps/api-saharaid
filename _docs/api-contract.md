# Target API Contract — Saharaid Backoffice

## 1. Status

This is the target contract for the new AWS backend. Paths are relative to the API Gateway HTTP API base URL. The previous Supabase handlers were unreleased; the existing business routes and payloads are retained where the service change allows.

The `ts` blocks below describe JSON field names and types; they are documentation only. Clients send ordinary JSON, and the backend is Python.

Certificate APIs are out of scope.

## 2. Conventions

### 2.1 Authentication

- `POST /register` is deprecated and is not deployed. Backoffice users are created manually in Cognito and PostgreSQL.
- `POST /login`, `POST /login/new-password`, and `POST /login/refresh` call Cognito through the backend and do not require a bearer token.
- Every business endpoint requires `Authorization: Bearer <Cognito access token>`.
- API Gateway HTTP API validates the JWT. Lambda verifies that it is an access token, obtains the Cognito user's email, and resolves a matching backoffice user by email in PostgreSQL before business logic runs.
- All provisioned backoffice users have the same access in this phase; roles are deferred. Email changes require coordinated administrator updates in Cognito and PostgreSQL.
- Sanity write tokens, database credentials, privileged AWS credentials, and raw password data are never returned.

### 2.2 JSON and naming

- JSON fields and query parameters use `snake_case`, except the preserved authentication response field `refreshToken`.
- UUID fields contain PostgreSQL entity IDs.
- Fields ending in `_sanity_id` contain Sanity string document IDs and must not be parsed as UUIDs.
- Empty optional fields use `null` or are omitted as stated; empty strings are not substitutes for missing values.

### 2.3 Date and time

- Date-only values use `YYYY-MM-DD`.
- Timestamps use RFC 3339 and represent GMT+7 (`Asia/Jakarta`) business time.
- Today, Yesterday, rolling filters, and schedule batch years use GMT+7.

### 2.4 Errors

```ts
type ErrorResponse = {
  error: string;
  errCode: string;
  details?: Array<{
    row?: number;
    field?: string;
    message: string;
  }>;
};
```

Common statuses:

| Status | Meaning                                                     |
| ------ | ----------------------------------------------------------- |
| 400    | Invalid body, query, file metadata, or pagination           |
| 401    | Missing, invalid, or expired access token                   |
| 403    | Valid Cognito identity without a matching backoffice user   |
| 404    | Requested active entity does not exist                      |
| 409    | Unique conflict, duplicate enrollment, or referenced option |
| 413    | Bulk/file count or declared file size exceeds its limit     |
| 500    | Database or internal failure                                |
| 502    | S3 or Sanity operation failed                               |

### 2.5 Pagination

Every main-list endpoint accepts:

```ts
type PaginationQuery = {
  p?: number; // integer >= 1, default 1
  rp?: number; // integer from 1 to 100, default 12
};
```

Every paginated JSON response uses:

```ts
type Paginated<T> = {
  data: T[];
  pagination: {
    p: number;
    rp: number;
    total: number;
  };
};
```

The database performs filtering, sorting, pagination, and the exact count. List rows contain only screen-level fields.

## 3. Authentication

There is no `POST /register` route.

### POST `/login`

```ts
type LoginRequest = {
  email: string;
  password: string;
};
```

Lambda calls Cognito `AdminInitiateAuth` through boto3. A normal login returns `200`:

```ts
type LoginSuccess = {
  user: { id: string; name: string; email: string }; // PostgreSQL UUID and profile
  token: string; // Cognito access token
  refreshToken: string; // Cognito refresh token
};
```

If Cognito requires a new password, `POST /login` returns `200` with no tokens:

```ts
{
  challenge: "NEW_PASSWORD_REQUIRED";
  email: string;
  session: string; // opaque Cognito challenge session
}
```

The frontend displays a new-password form and keeps the opaque challenge session only until that flow completes. The session must not be logged. Cognito user creation suppresses the invitation email; an administrator passes the temporary password to the teammate through a secure channel.

### POST `/login/new-password`

```ts
{
  email: string;
  session: string; // returned by POST /login
  new_password: string;
}
```

Lambda calls Cognito `AdminRespondToAuthChallenge` with `NEW_PASSWORD_REQUIRED`. On success it checks for the matching PostgreSQL user and returns `LoginSuccess` with `200`. Invalid or expired challenge sessions return `401`; passwords rejected by the Cognito password policy return `400`.

### POST `/login/refresh`

```ts
{
  refreshToken: string;
}
```

Lambda asks Cognito for a new access token, checks the matching PostgreSQL user, and returns `200`:

```ts
{
  token: string;
  refreshToken: string;
}
```

If Cognito rotates the refresh token, the response contains the replacement. Otherwise it returns the existing token. Cognito controls both token lifetimes; the backend does not store either token. Invalid or expired refresh tokens return `401`.

The Cognito pool uses email as the sign-in identifier and is provisioned with each user's email so no additional required attributes interrupt the new-password challenge. Only administrators may change user email, and they must update Cognito and PostgreSQL together. Without email delivery, forgotten passwords and expired temporary passwords are reset manually by an administrator.

## 4. Shared data types

```ts
type Participant = {
  id: string;
  serial_number: number;
  name: string;
  identity_number: string;
  gender: string;
  phone_number: string;
  email: string;
  date_of_birth: string;
  religion: string;
  address: string;
  job_position: string;
  job_company: string;
  education: string;
  cr_number: string;
  tax_number: string;
  created_at: string;
  updated_at: string | null;
};

type DocumentMetadata = {
  id: string;
  document_type: string;
  original_filename: string;
  content_type: string;
  file_size: number;
  last_modified_at: string;
  uploaded_at: string;
};

type Instructor = {
  id: string;
  name: string;
  phone_number: string;
  email: string;
  expertise: string;
  course_theme: {
    id: string;
    sanity_id: string;
    title: string;
    slug: string;
  };
  created_at: string;
  updated_at: string | null;
};

type Schedule = {
  id: string;
  course_id: string;
  course_title: string;
  class: string;
  course_mode: "online" | "offline";
  start_date: string;
  end_date: string;
  location: string;
  batch: number;
  batch_year: number;
  participant_count: number;
  created_at: string;
  updated_at: string | null;
};
```

## 5. Participants

### GET `/participant`

Query:

```ts
{
  p?: number;
  rp?: number;
  created?:
    | "last_hour"
    | "today"
    | "yesterday"
    | "last_7_days"
    | "last_30_days"
    | "last_90_days"
    | "last_365_days";
  sort?: "oldest" | "newest" | "name_asc" | "name_desc";
}
```

Default sort is `newest`. Success — `200`:

```json
  {
    "id" : str,
    "serial_number" : str,
    "name" : str,
    "phone_number" : str,
    "email" : str,
    "created_at": str,
  }
```

The list never contains documents or signed URLs.

### GET `/participant/{id}`

Success — `200`:

```ts
{
  participant: Participant;
  documents: DocumentMetadata[];
}
```

Document metadata does not include `s3_key` or a signed URL.

### POST `/participant`

### PUT `/participant?id={uuid}`

Both use:

```ts
type ParticipantPayload = Omit<
  Participant,
  "id" | "serial_number" | "created_at" | "updated_at"
>;
```

`POST` returns `{ participant: Participant }` with `201`; `PUT` returns it with `200`.

Names are trimmed and unique among active participants using case-insensitive comparison. Phone numbers are trimmed and unique among active participants without other normalization. Soft-deleted rows do not reserve either value. A conflict returns `409 PARTICIPANT_ALREADY_EXISTS`.

### DELETE `/participant?id={uuid}`

Soft-deletes the participant. Success — `200`:

```ts
{
  participant: Participant;
}
```

Its serial number is never reused.

### POST `/participant/bulk`

```ts
type ParticipantBulkRequest = {
  headers: Array<keyof ParticipantPayload>;
  data: unknown[][]; // maximum 200 rows
};
```

The backend rejects duplicate headers, unknown headers, unequal row lengths, more than 200 rows, invalid values, and duplicate active name/phone values. Validation includes conflicts within the request itself.

The operation is atomic. Success — `201`:

```ts
{
  inserted: number;
}
```

Any failure inserts zero participants and returns `400` or `409` with row-level `details`.

### GET `/participant/export`

Accepts the same `created` and `sort` query parameters as the list, without `p` or `rp`.

Success — `200` with content type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` and an `.xlsx` attachment. Documents and file metadata are excluded.

### GET `/participant/course-history?id={uuid}`

Query:

```ts
{
  id: string;
  p?: number;
  rp?: number;
  course_name?: string;
  course_theme_id?: string; // local PostgreSQL UUID
  sort?: "oldest" | "newest" | "name_asc" | "name_desc";
}
```

Success — `200`:

```ts
Paginated<{
  enrollment_id: string;
  enrolled_at: string;
  schedule_id: string;
  batch: number;
  start_date: string;
  end_date: string;
  course_id: string;
  course_sanity_id: string;
  course_title: string;
  course_themes: Array<{ id: string; title: string; slug: string }>;
}>;
```

Search applies to course title only.

## 6. Files and document metadata

### POST `/files/presign-upload`

```ts
type PresignUploadRequest = {
  owner: {
    type: "participant" | "instructor" | "course";
    id: string;
  };
  files: Array<{
    filename: string;
    content_type: string;
    file_size: number;
    document_type?: string; // participant/instructor only
    asset_type?: "gallery" | "brochure"; // course only
  }>;
};
```

The backend verifies the active owner, count, declared type, and declared size before signing. Course requests allow at most six gallery images. Success — `200`:

```ts
{
  files: Array<{
    s3_key: string;
    upload_url: string;
  }>;
  expires_in: number;
}
```

The frontend uploads bytes directly to each URL.

### POST `/documents`

Records participant or instructor document metadata after direct upload.

```ts
type DocumentsRequest = {
  owner: {
    type: "participant" | "instructor";
    id: string;
  };
  documents: Array<{
    document_type: string;
    s3_key: string;
    original_filename: string;
    content_type: string;
    file_size: number;
    last_modified_at: string;
  }>;
  remove_ids?: string[];
};
```

The backend verifies ownership and performs S3 `HEAD` for every new object. The actual content type and size must match the allowed slot and request metadata. Additions and removals are committed as one metadata operation. Success — `200`:

```ts
{ documents: DocumentMetadata[] }
```

Participant slots are optional and accept at most one file per document type. Instructor supports one optional PDF `curiculum_vitae`. Every file is limited to 1 MiB.

### POST `/files/presign-download`

```ts
{
  owner_type: "participant" | "instructor";
  document_id: string;
}
```

The backend resolves the S3 key from PostgreSQL after authorization; clients cannot submit a raw S3 key. Success — `200`:

```ts
{
  download_url: string;
  expires_in: number;
}
```

## 7. Instructors

### GET `/instructor`

Query:

```ts
{
  p?: number;
  rp?: number;
  course_theme_id?: string;
  sort?: "oldest" | "newest" | "name_asc" | "name_desc";
}
```

Success — `200`:

```ts
Paginated<
  Instructor & {
    document: (DocumentMetadata & { available: true }) | null;
  }
>;
```

No signed URL is generated by the list.

### GET `/instructor?id={uuid}`

Success — `200`:

```ts
{
  instructor: Instructor;
  document: DocumentMetadata | null;
}
```

### POST `/instructor`

### PUT `/instructor?id={uuid}`

```ts
type InstructorPayload = {
  name: string;
  phone_number: string;
  email: string;
  course_theme_id: string;
  expertise: string;
};
```

The course-theme ID is the local PostgreSQL UUID. `POST` returns `{ instructor: Instructor }` with `201`; `PUT` returns it with `200`.

## 8. Course reference options

Supported resources:

```ts
type CourseResource =
  | "courseTheme"
  | "courseType"
  | "courseClassType"
  | "courseCertificateValidity";
```

### GET `/course?resource={CourseResource}`

Returns all compact options for globally cached selectors. Success — `200`:

```ts
{
  options: Array<{
    id: string; // local PostgreSQL UUID
    sanity_id: string;
    title: string;
    slug?: string; // courseTheme
    code?: string; // courseType
  }>;
}
```

### POST `/course?resource={CourseResource}`

Creates the Sanity option and its PostgreSQL mirror.

```ts
type CourseOptionRequest = {
  title: string;
  slug?: string; // required for courseTheme
  code?: string; // required for courseType
};
```

Success — `201`: `{ option: ... }` using the GET option shape.

### DELETE `/course?resource={CourseResource}&id={uuid}`

`id` is the local PostgreSQL UUID. The backend rejects referenced options with `409 OPTION_IN_USE`, then deletes from Sanity and PostgreSQL. Success — `200` with `{}`.

## 9. Courses

The frontend reads paginated course lists and rich course detail directly from Sanity. There is no backend course-list endpoint.

### POST `/course`

Creates course metadata without file bytes.

```ts
type CoursePayload = {
  title: string;
  slug: string;
  theme_sanity_ids: string[];
  course_type_sanity_id: string;
  course_class_type_sanity_id: string;
  course_certificate_validity_sanity_id: string;
  course_mode: Array<"online" | "offline">;
  duration: string;
  overview: unknown[];
  objective: unknown[];
  outline: unknown[];
  requirement: unknown[];
  related_course_sanity_ids: string[];
  recommended_for: Array<"fresh-graduate" | "experienced" | "student">;
};
```

The backend validates every Sanity reference, creates the Sanity document, and inserts its PostgreSQL mirror and theme relationships. Success — `201`:

```ts
{
  course: {
    id: string;
    sanity_id: string;
    title: string;
    asset_status: "pending" | "ready";
  }
}
```

`asset_status` is `ready` when no course assets are expected; otherwise it remains `pending` until finalization.

### PUT `/course?id={uuid}`

Uses `CoursePayload` and updates the existing Sanity document, PostgreSQL mirror, and theme relationships. File fields remain unchanged. Success — `200` with the same course shape as POST.

### POST `/course/finalize?id={uuid}`

Finalizes staged S3 assets. Omitting a property leaves that asset field unchanged during edit. Providing `gallery` replaces the complete gallery; providing `brochure` replaces or removes the brochure.

```ts
type StagedAsset = {
  s3_key: string;
  original_filename: string;
  content_type: string;
  file_size: number;
};

type CourseFinalizeRequest = {
  gallery?: StagedAsset[]; // 0..6 JPEG/PNG files, each <= 1 MiB
  brochure?: StagedAsset | null; // PDF <= 1 MiB; null removes it
};
```

The backend performs S3 `HEAD`, streams each object from S3 to Sanity without buffering, patches the course, deletes replaced Sanity assets, marks the mirror `ready`, and immediately deletes successfully finalized S3 objects.

The operation is idempotent for the same course and S3 keys. Success — `200`:

```ts
{
  course: {
    id: string;
    sanity_id: string;
    asset_status: "ready";
  }
}
```

## 10. Schedules

### GET `/schedule`

Query:

```ts
{
  p?: number;
  rp?: number;
  course_theme_id?: string;
  sort?: "oldest" | "newest" | "name_asc" | "name_desc";
}
```

`name_asc` and `name_desc` sort by course title. Success — `200`: `Paginated<Schedule>`.

### GET `/schedule?id={uuid}`

Success — `200`:

```ts
{
  schedule: Schedule;
  participants: Array<
    Pick<
      Participant,
      "id" | "serial_number" | "name" | "phone_number" | "email"
    >
  >;
}
```

### POST `/schedule`

```ts
type SchedulePayload = {
  course_id: string;
  class: string;
  course_mode: "online" | "offline";
  start_date: string;
  end_date: string;
  location: string;
};
```

PostgreSQL assigns `batch` atomically from the GMT+7 year of `start_date`. Success — `201`: `{ schedule: Schedule }`.

### PUT `/schedule?id={uuid}`

```ts
type ScheduleUpdateRequest = SchedulePayload & {
  deleted_participant_ids?: string[];
};
```

Schedule changes and enrollment removals are committed together. Changing `start_date` to another year allocates the next batch in that year; changing it within the same year preserves the batch. Success — `200`: `{ schedule: Schedule }`.

### DELETE `/schedule?id={uuid}`

Soft-deletes the schedule without reusing its batch. Success — `200`: `{ schedule: Schedule }`.

## 11. Enrollments

### GET `/enrollment`

Query:

```ts
{
  p?: number;
  rp?: number;
  sort?: "oldest" | "newest" | "name_asc" | "name_desc";
}
```

Name sorting uses participant name. Success — `200`:

```ts
Paginated<{
  id: string;
  enrolled_at: string;
  participant: Pick<
    Participant,
    "id" | "serial_number" | "name" | "phone_number" | "email"
  >;
  schedule: Pick<
    Schedule,
    | "id"
    | "course_id"
    | "course_title"
    | "class"
    | "batch"
    | "start_date"
    | "end_date"
  >;
}>;
```

### POST `/enrollment`

```ts
{
  schedule_id: string;
  participant_ids: string[];
}
```

Adds all selected active participants in one database operation. Any invalid participant or duplicate active enrollment rejects the complete request. Success — `201`:

```ts
{
  inserted: number;
}
```

Enrollment removal is handled by `PUT /schedule?id={uuid}` with `deleted_participant_ids`.

## 12. File constraints

### Participant documents

| `document_type`          | Accepted content types                       | Maximum size |
| ------------------------ | -------------------------------------------- | ------------ |
| `passport_photo`         | `image/jpeg`, `image/png`                    | 1 MiB        |
| `identity_card`          | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB        |
| `tax_number`             | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB        |
| `curiculum_vitae`        | `application/pdf`                            | 1 MiB        |
| `employment_certificate` | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB        |
| `medical_certificate`    | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB        |
| `integrity_pact`         | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB        |
| `degree_certificate`     | `image/jpeg`, `image/png`, `application/pdf` | 1 MiB        |

All slots are optional.

### Other files

| Owner/slot                   | Accepted content types    | Maximum size/count    |
| ---------------------------- | ------------------------- | --------------------- |
| Instructor `curiculum_vitae` | `application/pdf`         | 1 MiB, one file       |
| Course gallery               | `image/jpeg`, `image/png` | 1 MiB each, six files |
| Course brochure              | `application/pdf`         | 1 MiB, one file       |
