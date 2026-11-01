FROM python:3.12.12-slim
WORKDIR /app
COPY labs/housing/requirements.txt labs/housing/pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt
COPY labs/housing/src ./src
RUN pip install --no-cache-dir --no-deps . && useradd --uid 10001 --create-home student
COPY modules/tasks.json /course/modules/tasks.json
COPY modules/01-ml/tasks /course/modules/01-ml/tasks
COPY modules/02-reproducibility/tasks /course/modules/02-reproducibility/tasks
ENV MLOPS_COURSE_ROOT=/course
USER 10001
ENV MODEL_PATH=/models/model.joblib
EXPOSE 8000
CMD ["uvicorn", "housing.api:app", "--host", "0.0.0.0", "--port", "8000"]
