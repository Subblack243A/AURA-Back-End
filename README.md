# AURA Backend - API de Bienestar Emocional

Este es el backend de **AURA**, una plataforma de bienestar emocional que utiliza Inteligencia Artificial para el análisis de sentimientos y reconocimiento facial. Construido con **Django Rest Framework** y **DeepFace**.

## 🚀 Tecnologías Principales

*   **Django & DRF**: Framework principal para la API REST.
*   **PostgreSQL + pgvector**: Base de datos relacional con soporte para vectores de alta dimensión (embeddings faciales).
*   **DeepFace**: Librería de IA para el reconocimiento facial y análisis de emociones (utiliza modelos como ArcFace).
*   **Docker & Docker Compose**: Para una orquestación y despliegue consistentes.

## 📂 Estructura del Proyecto

```text
api/
├── models/tables/      # Definición de modelos de base de datos
├── serializers/        # Transformación de datos (JSON <-> Modelos)
├── services/           # Lógica de negocio pesada (DeepFaceService)
├── views/              # Endpoints de la API
├── urls.py             # Definición de rutas
└── migrations/         # Historial de cambios en la base de datos
AuraBackend/            # Configuración del proyecto Django (settings.py)
manage.py               # Herramienta de gestión de Django
Dockerfile              # Configuración de imagen de contenedor
docker-compose.yml      # Definición de servicios (Backend + DB)
```

## 📊 Modelos de Datos Relevantes

*   **UserModel**: Extiende el usuario base de Django para incluir un `VectorField` de 512 dimensiones para el embedding facial y campos académicos (Semestre, Facultad, Programa).
*   **RecognitionModel**: Almacena los resultados históricos del análisis de emociones asociados a cada usuario.
*   **EmotionRegisterModel**: Almacena las emociones registradas por el usuario.
*   **SurveyModel & SurveyResultModel**: Sistema para gestionar encuestas de bienestar y sus respuestas.
*   **DictionaryModels**: Tablas maestras para roles, programas, facultades y emociones.

## 🛠️ Requerimientos y Ejecución

### Requisitos Previos

*   **Docker** y **Docker Compose** instalados.
*   Cámara web funcional (para las pruebas con el frontend).

### Pasos para Ejecutar

1.  **Configurar Variables de Entorno**: Crea un archivo `.env` en la raíz basado en los valores de `settings.py` (DB_NAME, DB_USER, etc.).
2.  **Iniciar Servicios**:
    ```bash
    docker-compose up --build
    ```
3.  **Aplicar Migraciones**:
    ```bash
    docker-compose exec aura_backend python manage.py migrate
    ```

## 🧠 Flujo de Autenticación Facial

1.  El usuario envía sus credenciales y una imagen.
2.  Si el usuario no tiene rostro registrado, el sistema genera un **embedding** y lo guarda en Postgres.
3.  Si ya existe un registro, se compara el nuevo rostro con el guardado usando **distancia del coseno**.
4.  Tras una verificación exitosa, se procede al **análisis de emociones** y se guarda la captura en el dataset categorizado.
