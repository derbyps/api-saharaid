from enum import StrEnum


class FileContentTypes(StrEnum):
    EXCEL = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    CSV = "text/csv"
    XML = "application/xml"
