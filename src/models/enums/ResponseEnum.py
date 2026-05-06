from enum import Enum
class ResponseSignal(Enum):
    FILE_TYPE_ERROR="File not supported"
    FILE_SIZE_LIMIT="File limit exceed"
    FILE_UPLOADED_SUCCESSFULLY="File uploaded successfully"
    ERROR_UPLOADING="Error uplaoding file"
    PROCESSING_SUCCESS = "Processing success"
    PROCESSING_FAILED = "Processing failed"
