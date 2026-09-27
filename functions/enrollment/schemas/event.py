from datetime import date
from typing import NotRequired, TypedDict


class GetEnrollmentsParams(TypedDict):
    p: NotRequired[int]
    rp: NotRequired[int]
    search: NotRequired[str]


class CreateEnrollmentBody(TypedDict):
    name: str
    identity_number: str
    gender: str
    phone_number: str
    email: str
    date_of_birth: date
    religion: str
    address: str
    job_position: str
    job_company: str
    education: str
    cr_number: str
    tax_number: str
