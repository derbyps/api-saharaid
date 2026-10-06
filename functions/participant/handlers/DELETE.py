from shared import util

from ..services.participant import ParticipantService


def delete_method_handler(event: dict) -> dict:
    participant_id = (event.get("pathParameters") or {}).get("id")
    if not participant_id:
        return util.return_response(400, {})

    service = ParticipantService()
    participant = service.delete(participant_id, event)

    return util.return_response(
        200,
        {
            "participant": {
                "id": participant.id,
                "name": participant.name,
                "identity_number": participant.identity_number,
                "gender": participant.gender,
                "phone_number": participant.phone_number,
                "email": participant.email,
                "date_of_birth": participant.date_of_birth,
                "religion": participant.religion,
                "address": participant.address,
                "job_position": participant.job_position,
                "job_company": participant.job_company,
                "education": participant.education,
                "cr_number": participant.cr_number,
                "tax_number": participant.tax_number,
            }
        },
    )
