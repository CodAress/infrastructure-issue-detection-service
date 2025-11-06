# ==========================================
# Multi-Stage Dockerfile - Infrastructure Issue Detection Service
# Optimizado para seguridad y tamaño reducido
# ==========================================

# ==========================================
# STAGE 1: Builder - Compilar dependencias
# ==========================================
FROM python:3.11-slim AS builder

# Evitar preguntas interactivas durante instalación
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /build

# Copiar solo requirements.txt primero (aprovecha cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python en un directorio aislado
RUN pip install --user --no-warn-script-location -r requirements.txt

# ==========================================
# STAGE 2: Runtime - Imagen final (sin código fuente visible)
# ==========================================
FROM python:3.11-slim

# Metadatos de la imagen
LABEL maintainer="CodAress" \
      version="1.0.0" \
      description="Infrastructure Issue Detection Service with YOLO" \
      security.scan="true"

# Variables de entorno de seguridad
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    # Seguridad: Deshabilitar bytecode para dificultar ingeniería inversa
    PYTHONOPTIMIZE=2 \
    # Usuario no-root
    APP_USER=appuser \
    APP_HOME=/app

# Instalar solo dependencias de runtime (sin herramientas de compilación)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para mayor seguridad
RUN groupadd -r ${APP_USER} && \
    useradd -r -g ${APP_USER} -d ${APP_HOME} -s /sbin/nologin ${APP_USER}

# Crear directorios necesarios
RUN mkdir -p ${APP_HOME}/models ${APP_HOME}/logs && \
    chown -R ${APP_USER}:${APP_USER} ${APP_HOME}

# Copiar dependencias Python desde builder
COPY --from=builder --chown=${APP_USER}:${APP_USER} /root/.local /home/${APP_USER}/.local

# Establecer directorio de trabajo
WORKDIR ${APP_HOME}

# Copiar código de la aplicación (se compilará a bytecode)
COPY --chown=${APP_USER}:${APP_USER} . .

# 🔒 SEGURIDAD: Compilar código Python a bytecode y eliminar .py
# Esto dificulta la extracción del código fuente
RUN python -m compileall -b . && \
    find . -type f -name '*.py' ! -name 'app.py' -delete && \
    find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# Configurar PATH para usar paquetes del usuario
ENV PATH=/home/${APP_USER}/.local/bin:$PATH

# Cambiar a usuario no-root
USER ${APP_USER}

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/v1/health', timeout=5)" || exit 1

# Comando de inicio
CMD ["python", "app.py"]
