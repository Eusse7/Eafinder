import os

# Angular corre en 4200 con `ng serve`.
# Se puede sobreescribir con CORS_ALLOWED_ORIGINS en el .env, separando por comas.
_default = "http://localhost:4200,http://127.0.0.1:4200"

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", _default).split(",")
    if origin.strip()
]
