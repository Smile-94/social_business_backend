from apps.common.dataclass import ResponseClient, SuccessResponse

CREATED_SUCCESS = SuccessResponse(
    status=201,
    type="success",
    message="201 Created",
    client=ResponseClient.USER,
    data={},
).model_dump()
