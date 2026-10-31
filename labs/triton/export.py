"""Упражнение 15: экспорт собственного Pipeline и parity с ONNX Runtime."""
from pathlib import Path
import joblib
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
bundle = joblib.load("work/artifacts/model.joblib")
# TODO(student): convert with FloatTensorType([None, 8]), target_opset=17,
# save model.onnx in labs/triton/model_repository/housing/1 and verify parity.
raise NotImplementedError("Реализуй экспорт и проверку численного совпадения")
