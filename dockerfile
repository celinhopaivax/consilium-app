CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.main:app", "--log-level", "debug"]
