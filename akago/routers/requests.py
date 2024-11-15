from fastapi import APIRouter, Response
from rich import print

from akago.models.request import AugmentationRequest

router = APIRouter(prefix="/requests")


@router.post("/")
def create_request(augmentation_request: AugmentationRequest) -> Response:
    # TODO: Handle the request.
    print(augmentation_request)

    return Response(status_code=200)
