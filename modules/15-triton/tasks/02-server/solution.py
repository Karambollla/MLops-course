"""HTTP V2 запрос; реальный сервер требует совместимого стенда."""

from course_tasks import load_task


def inference_request(
    rows: list[dict], feature_order: list[str], max_batch: int = 32
) -> dict:
    raise NotImplementedError(
        "Используй feature_matrix из 15-triton/01-onnx и собери HTTP V2 request"
    )
