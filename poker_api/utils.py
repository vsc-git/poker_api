from rest_framework.response import Response


def send_detail_response(message: str, status: int = 200) -> Response:
    return Response({"detail": message}, status=status)
