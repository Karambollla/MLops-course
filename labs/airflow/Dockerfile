FROM apache/airflow:3.1.0-python3.12
# Separate ML environment: do not overwrite Airflow's constrained dependencies.
USER root
RUN python -m venv /opt/housing-venv
COPY labs/housing/requirements.txt /tmp/housing-requirements.txt
RUN /opt/housing-venv/bin/pip install --no-cache-dir -r /tmp/housing-requirements.txt
COPY labs/housing /opt/housing
RUN /opt/housing-venv/bin/pip install --no-cache-dir --no-deps /opt/housing
USER airflow
