FROM apache/airflow:3.1.0-python3.12
# Separate ML environment: do not overwrite Airflow's constrained dependencies.
USER root
RUN python -m venv /opt/housing-venv
COPY labs/housing/requirements.txt /tmp/housing-requirements.txt
RUN /opt/housing-venv/bin/pip install --no-cache-dir -r /tmp/housing-requirements.txt
COPY labs/housing /opt/housing
RUN /opt/housing-venv/bin/pip wheel --no-cache-dir --no-deps --wheel-dir /tmp/housing-wheels /opt/housing \
    && /opt/housing-venv/bin/pip install --no-cache-dir --no-deps /tmp/housing-wheels/*.whl
USER airflow

COPY modules/tasks.json /course/modules/tasks.json
COPY modules/01-ml/housing.ipynb /course/modules/01-ml/housing.ipynb
COPY modules/02-reproducibility/tasks /course/modules/02-reproducibility/tasks
COPY modules/05-airflow/tasks /course/modules/05-airflow/tasks
ENV MLOPS_COURSE_ROOT=/course
# Scheduler only needs the pure-Python loader; ML dependencies stay in the separate venv.
RUN pip install --no-cache-dir --no-deps /tmp/housing-wheels/*.whl
