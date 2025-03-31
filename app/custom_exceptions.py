from fastapi import HTTPException


# make custom error extend to HTTPException, they are treated as HTTP exceptions by FastAPI.
# When these exceptions are raised, FastAPI will always catch them ON MOST OUTER LEVEL
# automatically convert them into a HTTP responses with the appropriate status code and detail message as payload json with "detail".
class GeneralServerError(HTTPException):
    def __init__(self, error_detail_message: str):
        super().__init__(status_code=500, detail=error_detail_message)


class FileTypeNotSupportedError(HTTPException):
    def __init__(self, error_detail_message: str):
        super().__init__(status_code=500, detail=error_detail_message)


class NoneJobSiteError(HTTPException):
    def __init__(self, error_detail_message: str):
        super().__init__(status_code=400, detail=error_detail_message)


class NotEnoughCreditsError(HTTPException):
    def __init__(self, error_detail_message: str):
        super().__init__(status_code=402, detail=error_detail_message)


class InvalidPackageError(HTTPException):
    def __init__(self, error_detail_message: str):
        super().__init__(status_code=400, detail=error_detail_message)
