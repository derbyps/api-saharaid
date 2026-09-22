from typing import NotRequired, TypedDict


class GetParticipantsParams(TypedDict):
    p: NotRequired[int]
    rp: NotRequired[int]
    search: NotRequired[str]


# def parse_body(event: dict) -> dict:
#     body = event.get("body")
#     try:
#         if event.get("isBase64Encoded"):
#             body = base64.b64decode(body, validate=True).decode("utf-8")
#         if isinstance(body, str):
#             body = json.loads(body)
#     except (TypeError, ValueError, UnicodeError, binascii.Error) as exc:
#         raise HttpError(400, "INVALID_BODY", "Request body must be valid JSON") from exc
#     if not isinstance(body, dict):
#         raise HttpError(400, "INVALID_BODY", "Request body must be a JSON object")
#     return body


# @dataclass(frozen=True)
# class CreateParticipantEventBody:
#     name: str
#     identity_number: str
#     gender: str
#     phone_number: str
#     email: str
#     date_of_birth: date
#     religion: str
#     address: str
#     job_position: str
#     job_company: str
#     education: str
#     cr_number: str
#     tax_number: str

#     @classmethod
#     def from_event(cls, event: dict):
#         body = parse_body(event)
#         names = {field.name for field in fields(cls)}
#         if body.keys() != names:
#             raise HttpError(
#                 400, "INVALID_BODY", "Participant fields are missing or unknown"
#             )
#         if any(not isinstance(body[name], str) for name in names):
#             raise HttpError(400, "INVALID_BODY", "Participant fields must be strings")
#         body["name"] = body["name"].strip()
#         body["phone_number"] = body["phone_number"].strip()
#         body["email"] = body["email"].strip()
#         if not body["name"] or not body["phone_number"] or not body["email"]:
#             raise HttpError(
#                 400, "INVALID_BODY", "Name, phone number, and email are required"
#             )
#         if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", body["date_of_birth"]):
#             raise HttpError(400, "INVALID_BODY", "date_of_birth must be YYYY-MM-DD")
#         try:
#             body["date_of_birth"] = date.fromisoformat(body["date_of_birth"])
#         except ValueError as exc:
#             raise HttpError(
#                 400, "INVALID_BODY", "date_of_birth must be YYYY-MM-DD"
#             ) from exc
#         return cls(**body)

#     def values(self) -> dict:
#         return {field.name: getattr(self, field.name) for field in fields(self)}


# def participant_id(event: dict) -> UUID:
#     value = (event.get("queryStringParameters") or {}).get("id")
#     try:
#         return UUID(value)
#     except (TypeError, ValueError) as exc:
#         raise HttpError(400, "INVALID_ID", "id must be a UUID") from exc


# def list_query(event: dict) -> tuple[int, int, str | None, str]:
#     query = event.get("queryStringParameters") or {}
#     try:
#         page = int(query.get("p", "1"))
#         rows = int(query.get("rp", "12"))
#     except (TypeError, ValueError) as exc:
#         raise HttpError(400, "INVALID_PAGINATION", "p and rp must be integers") from exc
#     if page < 1 or not 1 <= rows <= 100:
#         raise HttpError(
#             400, "INVALID_PAGINATION", "p must be >= 1 and rp must be 1..100"
#         )
#     created = query.get("created")
#     if created not in {
#         None,
#         "last_hour",
#         "today",
#         "yesterday",
#         "last_7_days",
#         "last_30_days",
#         "last_90_days",
#         "last_365_days",
#     }:
#         raise HttpError(400, "INVALID_FILTER", "Invalid created filter")
#     sort = query.get("sort", "newest")
#     if sort not in {"oldest", "newest", "name_asc", "name_desc"}:
#         raise HttpError(400, "INVALID_SORT", "Invalid sort")
#     return page, rows, created, sort
