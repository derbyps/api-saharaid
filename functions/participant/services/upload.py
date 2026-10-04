import os
import tempfile

import pandas as pd

from shared.constant.storage import StorageFolder
from shared.modules.Storage.storage_service import StorageService


class UploadService:
    def __init__(self):
        pass

    def to_s3(self, data_export: list) -> str:

        file_name = "Data participant"
        pd_dataframe = pd.json_normalize(data_export)

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp:
            with pd.ExcelWriter(temp.name, engine="openpyxl") as writer:
                pd_dataframe.to_excel(writer, index=False)

            # Read the file into a BytesIO object
            with open(temp.name, "rb") as f:
                data = f.read()

        storage_service = StorageService(os.environ["S3_BUCKET"])
        url = storage_service.upload_excel(data, StorageFolder.PARTICIPANT, file_name)

        os.remove(temp.name)  # Delete the temporary file

        return url
