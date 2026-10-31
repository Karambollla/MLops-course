# MLOps Course Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Создать полный русскоязычный курс с интенсивом, лабораторными и проектом.

**Architecture:** Markdown-модули, самостоятельные стенды и общий CPU-проект. Отдельные маршруты для Mac и NVIDIA.

**Tech Stack:** Python, MLflow, Airflow, ClearML, Kubernetes, Helm, мониторинг, Vault, IaC, search и serving.

**Spec:** [Согласованная спецификация](../specs/2026-10-31-mlops-course-design.md).

## Global Constraints

- Русский язык; Python 3.12; Mac ARM64, 16 ГБ RAM, без NVIDIA GPU.
- Обязательная практика без платных сервисов; стартовые файлы без полных решений.
- Интенсив 14 дней по 6–8 часов и маршрут 7 дней.

## Review Focus

ARM64-совместимость, RAM, версии, проверяемые критерии, покрытие инструментов.

## Tasks

- [x] Task 1: Каркас, диагностика, окружение, источники и навигация.
- [x] Task 2: Python, ML, воспроизводимость, API/Docker/CI и стартовый проект.
- [x] Task 3: MLflow, Airflow, ClearML, отдельные стенды и сбои.
- [x] Task 4: Kubernetes, Helm, мониторинг, Vault, Terraform и Ansible.
- [x] Task 5: Qdrant, Elasticsearch/OpenSearch, Triton и LLM-serving.
- [x] Task 6: Проект, шаблоны отчётов и подготовка к работе.
- [x] Final: Проверки материалов, конфигураций, свежий обзор и отчёт.

Каждый Task заканчивается проверкой наличия материалов и соответствия контрактов. Команды итоговой проверки: `make check`, `make test`, `docker compose -f FILE config --quiet`, `helm lint`, `terraform validate`, `ansible-playbook --syntax-check`. Недоступные runtime-проверки фиксируются явно.
