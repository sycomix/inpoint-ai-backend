from fastapi import status
from pydantic import Field


class ResponseModel:

    @staticmethod
    def return_response(data, message: str = Field(...)):
        return {
            'data': data,
            'code': status.HTTP_200_OK,
            'message': message
        }


class ErrorResponseModel:

    @staticmethod
    def return_response(error: str = Field(...), code: status = Field(...), message: str = Field(...)):
        return {
            'error': error,
            'code': code,
            'message': message
        }
