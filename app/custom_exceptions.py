from fastapi import HTTPException


# extend HTTPException, they are treated as HTTP exceptions by FastAPI.
# When these exceptions are raised, FastAPI will automatically convert them into HTTP responses with the appropriate status code and detail message.
class GeneralServerError(HTTPException):
    def __init__(self, detail_message: str):
        super().__init__(status_code=500, detail=detail_message)


class FileTypeNotSupportedError(HTTPException):
    def __init__(self, detail_message: str):
        super().__init__(status_code=500, detail=detail_message)


class NoneJobSiteError(HTTPException):
    def __init__(self, detail_message: str):
        super().__init__(status_code=400, detail=detail_message)
