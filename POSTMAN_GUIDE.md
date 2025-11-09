# 📮 Guía de Postman - Infrastructure Detection Service API

## 📥 Importar la Colección

1. **Abrir Postman**
2. Click en **"Import"** (esquina superior izquierda)
3. Arrastra el archivo `postman_collection.json` o selecciónalo manualmente
4. Click **"Import"**

## ⚙️ Configurar Variables de Entorno

Después de importar, configura las variables:

### Variables Disponibles:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `base_url` | URL base del servicio | `http://20.109.51.39` |
| `api_key` | API Key del cliente | `tu-api-key-generada` |
| `admin_api_key` | API Key de administrador | `admin-key-para-crear-clientes` |
| `client_id` | ID del cliente | `mi-backend-service` |
| `uuid_consulta` | UUID de ejemplo | `550e8400-e29b-41d4-a716-446655440000` |

### Pasos para configurar:

1. En Postman, click en el nombre de la colección
2. Tab **"Variables"**
3. Actualiza los valores en la columna **"Current Value"**
4. Click **"Save"**

## 🔐 Autenticación

Todos los endpoints (excepto health) requieren autenticación mediante **API Key en header**:

```
X-API-Key: tu-api-key-aqui
```

La colección está configurada para usar la variable `{{api_key}}` automáticamente.

## 📚 Estructura de la Colección

### 1️⃣ IAM - Gestión de Clientes

#### **GET** `/api/v1/clients/verify` - Verificar Credenciales
- Verifica que las credenciales del cliente sean válidas
- Requiere: Header `X-API-Key`

#### **GET** `/api/v1/clients/{client_id}` - Obtener Información del Cliente
- Obtiene información de un cliente específico
- Path param: `client_id`

---

### 2️⃣ Detección de Incidencias

#### **POST** `/api/v1/detecciones` - Crear Análisis
- Analiza una imagen para detectar incidencias
- Body requerido:
  ```json
  {
    "uuid_consulta": "UUID-generado-por-backend",
    "url_imagen": "https://ejemplo.com/imagen.jpg"
  }
  ```
- **Formatos soportados:** `.jpg`, `.jpeg`, `.png`
- Respuesta incluye:
  - Imagen procesada con anotaciones
  - Lista de detecciones con coordenadas
  - Nivel de confianza por detección

#### **GET** `/api/v1/detecciones/{uuid_consulta}` - Obtener Resultado
- Obtiene el resultado de un análisis específico
- Path param: `uuid_consulta`

#### **GET** `/api/v1/detecciones` - Listar Análisis
- Lista todos los análisis del cliente
- Query params opcionales:
  - `limit` (default: 50, max: 100)
  - `offset` (default: 0)

#### **POST** `/api/v1/detecciones/_batch/procesar` - Procesamiento por Lotes
- Procesa múltiples imágenes en un solo request
- Body requerido:
  ```json
  {
    "consultas": [
      {
        "uuid_consulta": "uuid-1",
        "url_imagen": "https://ejemplo.com/img1.jpg"
      },
      {
        "uuid_consulta": "uuid-2",
        "url_imagen": "https://ejemplo.com/img2.jpg"
      }
    ]
  }
  ```
- Retorna resumen con éxitos/fallos

## 🚀 Flujo de Uso Típico

### 1. Verificar Credenciales (Opcional)

```bash
GET /api/v1/clients/verify
Headers:
  X-API-Key: tu-api-key
```

### 2. Crear Análisis de Imagen

```bash
POST /api/v1/detecciones
Headers:
  X-API-Key: tu-api-key
Body:
{
  "uuid_consulta": "UUID-generado",
  "url_imagen": "https://url-publica/imagen.jpg"
}
```

### 3. Consultar Resultado (Si es necesario)

```bash
GET /api/v1/detecciones/{uuid}
Headers:
  X-API-Key: tu-api-key
```

## 📋 Ejemplos de Respuesta

### Análisis Exitoso (201)

```json
{
  "uuid_consulta": "550e8400-e29b-41d4-a716-446655440000",
  "url_imagen_original": "https://ejemplo.com/imagen.jpg",
  "url_imagen_procesada": "https://cloudinary.com/processed/imagen_550e8400.jpg",
  "estado": "completado",
  "fecha_creacion": "2025-11-08T21:00:00.000Z",
  "fecha_procesamiento": "2025-11-08T21:00:05.000Z",
  "detecciones": [
    {
      "clase": "Pothole",
      "confianza": 0.87,
      "bbox": {
        "x_min": 120,
        "y_min": 250,
        "x_max": 380,
        "y_max": 420
      }
    }
  ],
  "total_detecciones": 1,
  "tiempo_procesamiento_ms": 1250
}
```

### Procesamiento por Lotes (200)

```json
{
  "summary": {
    "total": 3,
    "exitosos": 2,
    "fallidos": 1
  },
  "resultados": [
    {
      "uuid_consulta": "uuid-1",
      "estado": "completado",
      "total_detecciones": 2
    },
    {
      "uuid_consulta": "uuid-2",
      "estado": "completado",
      "total_detecciones": 0
    },
    {
      "uuid_consulta": "uuid-3",
      "estado": "error",
      "mensaje": "URL de imagen no accesible"
    }
  ],
  "tiempo_total_ms": 4800
}
```

## ❌ Códigos de Error Comunes

| Código | Descripción | Solución |
|--------|-------------|----------|
| `400` | Datos inválidos | Verifica que `uuid_consulta` y `url_imagen` estén presentes y sean válidos |
| `401` | No autenticado | Verifica que el header `X-API-Key` sea correcto |
| `404` | No encontrado | Verifica que el UUID o cliente exista |
| `409` | UUID duplicado | El UUID ya fue usado anteriormente, usa uno nuevo |
| `500` | Error del servidor | Error procesando la imagen (formato, acceso, etc.) |

## 💡 Tips

1. **UUIDs únicos**: Cada `uuid_consulta` debe ser único. Genera un UUID v4 nuevo para cada análisis.
2. **URLs públicas**: Las imágenes deben estar en URLs públicamente accesibles (sin autenticación).
3. **Formatos soportados**: Solo `.jpg`, `.jpeg`, `.png`
4. **API Key segura**: Usa al menos 20 caracteres con letras, números y símbolos.
5. **Lotes grandes**: Para procesar muchas imágenes, usa el endpoint `/_batch/procesar` en lugar de múltiples requests individuales.

## 🔗 Variables de Entorno Sugeridas

Crea un **Environment** en Postman:

**Producción:**
```json
{
  "base_url": "http://20.109.51.39",
  "api_key": "{{TU_API_KEY_PRODUCCION}}",
  "admin_api_key": "{{ADMIN_KEY_PRODUCCION}}"
}
```

**Desarrollo Local:**
```json
{
  "base_url": "http://localhost:5000",
  "api_key": "test-api-key-local",
  "admin_api_key": "admin-test-key"
}
```

## 📞 Soporte

Para más información, consulta el repositorio:
https://github.com/CodAress/infrastructure-issue-detection-service
