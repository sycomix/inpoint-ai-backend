from fastapi import status
from pydantic import Field


class ResponseModel:

    @staticmethod
    def return_response(data: dict = Field(...)):
        return data


class ErrorResponseModel:

    @staticmethod
    def return_response(error: str = Field(...), code: status = Field(...), message: str = Field(...)):
        return {
            'error': error,
            'code': code,
            'message': message
        }
