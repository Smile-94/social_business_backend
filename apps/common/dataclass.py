# * PYDANTIC IMPORTS
from enum import Enum

from pydantic import BaseModel, Field, FilePath
from rest_framework import status as response_status


class ErrorType(str, Enum):
    WARNING = "warning"
    ERROR = "error"


class ResponseClient(str, Enum):
    DEVELOPER = "developer"
    USER = "user"


# <<------------------------------------Success Response---------------------------------------->>
class SuccessResponse(BaseModel):
    status: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Detailed error message")
    client: ResponseClient = Field(..., description="Client of the message")
    data: list | dict | None = Field(
        None,
        description="Additional information about the error",
    )
    links: dict | None = Field(
        default={"url": "https://www.example.com"},  # Example dictionary
        description="Quick access links for the next",
    )


class UpdateResponse(BaseModel):
    status: int = Field(..., description="HTTP status code")
    message: str = Field(..., description="Detailed error message")
    client: ResponseClient = Field(..., description="Client of the message")
    details: dict | None = Field(
        None,
        description="Additional information about success",
    )
    links: dict | None = Field(
        default={"url": "https://www.care-box.com"},  # Example dictionary
        description="Quick access links for the next",
    )


class ErrorResponse(BaseModel):
    status: int | None = Field(default=response_status.HTTP_400_BAD_REQUEST, description="HTTP status code")
    type: ErrorType | None = Field(default=ErrorType.WARNING, description="Error code indicating the type of error")
    message: str | None = Field(
        default="A Server Side Error Occurred While Processing your request", description="Detailed error message"
    )
    client: ResponseClient | None = Field(default=ResponseClient.DEVELOPER, description="Client error type")
    data: dict | None = Field(
        None,
        description="Additional information about the error",
    )


class NoContentResponse(BaseModel):
    status: int = Field(204, description="HTTP status code for successful deletion")
    alternate_status: int = Field(200, description="HTTP status code")
    message: str = Field(
        "Resource deleted successfully",
        description="Confirmation message for deletion",
    )
    client: ResponseClient = Field(..., description="Client of the message")
    description: dict | None = Field(
        None,
        description="Additional information about delete operation",
    )


class InvalidUrlResponse(BaseModel):
    status: int = Field(404, description="HTTP status code for successful deletion")
    message: str = Field(
        "404 Page Not Found",
        description="Message for page not found",
    )
    client: ResponseClient = Field(..., description="Client of the message")
    description: dict | None = Field(
        None,
        description="Additional information about invalid page url",
    )


class FileUploadResponse(BaseModel):
    file: FilePath = Field(..., description="Path to the uploaded file")
