from fastapi import HTTPException


class GeneralServerError(HTTPException):
    def __init__(self, detail_message: str):
        super().__init__(status_code=500, detail=detail_message)


class FileTypeNotSupportedError(HTTPException):
    def __init__(self, detail_message: str):
        super().__init__(status_code=500, detail=detail_message)


class NoneJobSiteError(HTTPException):
    def __init__(self, detail_message: str):
        super().__init__(status_code=400, detail=detail_message)
