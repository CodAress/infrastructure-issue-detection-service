# 📮 Guía de Postman - Infrastructure Detection Service API

## 📥 Importar la Colección

1. Abre Postman.
2. Click en "Import" (esquina superior izquierda).
3. Arrastra o selecciona `postman_collection.json` y haz click en "Import".

## ⚙️ Configurar Variables de Entorno

Después de importar, configura las variables de la colección (Collection > Variables) o crea un Environment con estas variables:

### Variables incluidas

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `base_url` | `http://detection-issue-service.eastus2.cloudapp.azure.com` | URL base del servicio en producción |
| `api_key` | `your-api-key-here` | API Key del cliente (reemplazar con tu key real) |
| `client_id` | `your-client-id` | ID del cliente (opcional) |
| `uuid_consulta` | `550e8400-e29b-41d4-a716-446655440000` | UUID de ejemplo para pruebas |

### Pasos rápidos

1. En Postman, selecciona la colección importada.
2. Ve a la pestaña "Variables" para ver/editar los valores.
3. O crea un nuevo Environment (Manage Environments) con estas variables.
4. Selecciona el Environment antes de ejecutar requests.

## 🔐 Autenticación

Todos los endpoints documentados requieren el header:

```
X-API-Key: {{api_key}}
```

La colección ya referencia `{{api_key}}` en los requests; actualiza su valor en el Environment o en las variables de la colección.

## 📚 Estructura de la Colección

La colección incluye dos carpetas principales:

### 1️⃣ IAM - Gestión de Clientes

Endpoints para autenticación y gestión de clientes:

#### GET `/api/v1/clients/verify` - Verificar Credenciales

Verifica que las credenciales del cliente sean válidas y estén activas.

**Headers requeridos:**
- `X-API-Key`: API Key del cliente

**Respuesta de ejemplo (200):**
```json
{
  "client": {
    "client_id": "mi-servicio-backend-2025",
    "is_active": true,
    "name": "Servicio Backend - Sistema de Gestión"
  },
  "message": "Credenciales válidas - Autenticación exitosa",
  "success": true
}
```

#### GET `/api/v1/clients/{client_id}` - Obtener Información del Cliente

Obtiene información pública de un cliente específico.

**Path params:**
- `client_id`: ID del cliente

**Headers requeridos:**
- `X-API-Key`: API Key válida

**Respuesta de ejemplo (200):**
```json
{
  "client": {
    "client_id": "mi-servicio-backend-2025",
    "is_active": true,
    "name": "Servicio Backend - Sistema de Gestión"
  },
  "success": true
}
```

---

### 2️⃣ Detección de Incidencias

Endpoints para análisis de imágenes y detección de incidencias:

#### POST `/api/v1/detecciones` - Crear Análisis

Crea una nueva solicitud de análisis de incidencias.

**Headers requeridos:**
- `X-API-Key`: API Key del cliente
- `Content-Type`: application/json

**Body (JSON):**
```json
{
  "uuid_consulta": "550e8400-e29b-41d4-a716-446655440001",
  "url_imagen": "https://i.ibb.co/ycKtjD3N/bache-01.jpg"
}
```

**Campos:**
- `uuid_consulta` (string UUID, requerido): UUID único generado por el backend principal
- `url_imagen` (string URL, requerido): URL pública de la imagen (.jpg, .jpeg, .png)

**Respuesta de ejemplo (201):**
```json
{
  "created_at": "2025-11-09T04:47:48.253398",
  "estado": "completado",
  "message": "Análisis procesado exitosamente",
  "success": true,
  "uuid_consulta": "550e8400-e29b-41d4-a716-446655440001"
}
```

#### GET `/api/v1/detecciones/{uuid_consulta}` - Obtener Resultado

Obtiene el resultado de un análisis específico mediante su UUID.

**Path params:**
- `uuid_consulta`: UUID de la consulta

**Headers requeridos:**
- `X-API-Key`: API Key del cliente

**Respuesta de ejemplo (200):**
```json
{
  "client_id": "mi-servicio-backend-2025",
  "created_at": "2025-11-09T03:44:25.810471",
  "estado": "completado",
  "resultado": {
    "categoria": "bache",
    "confianza": 0.9301,
    "detalles": {},
    "num_detecciones": 1,
    "timestamp": "2025-11-09T04:48:55.247472",
    "url_resultado": "https://res.cloudinary.com/example/detecciones/550e8400-e29b-41d4-a716-446655440000.png"
  },
  "updated_at": "2025-11-09T03:44:28.268933",
  "url_imagen": "https://i.ibb.co/ycKtjD3N/bache-01.jpg",
  "uuid_consulta": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### GET `/api/v1/detecciones?skip=0&limit=10` - Listar Análisis

Lista todos los análisis del cliente con paginación.

**Query params (opcionales):**
- `skip` (integer): Número de resultados a omitir (default: 0)
- `limit` (integer): Número máximo de resultados (default: 50)

**Headers requeridos:**
- `X-API-Key`: API Key del cliente

**Respuesta de ejemplo (200):**
```json
{
  "cliente": "mi-servicio-backend-2025",
  "limit": 10,
  "skip": 0,
  "solicitudes": [
    {
      "cliente": "mi-servicio-backend-2025",
      "created_at": "2025-11-09T03:44:25.810471",
      "estado": "completado",
      "resultado": {
        "categoria": "bache",
        "confianza": 0.9301,
        "detalles": {},
        "num_detecciones": 1,
        "timestamp": "2025-11-09T04:48:55.247472",
        "url_resultado": "https://res.cloudinary.com/example/detecciones/550e8400.png"
      },
      "updated_at": "2025-11-09T03:44:28.268933",
      "url_imagen": "https://i.ibb.co/ycKtjD3N/bache-01.jpg",
      "uuid_consulta": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "success": true,
  "total": 1
}
```

---

## 🚀 Flujo de Uso Típico

### 1. Verificar Credenciales (Opcional)

```bash
GET {{base_url}}/api/v1/clients/verify
Headers:
  X-API-Key: {{api_key}}
```

### 2. Crear Análisis de Imagen

```bash
POST {{base_url}}/api/v1/detecciones
Headers:
  X-API-Key: {{api_key}}
  Content-Type: application/json
Body:
{
  "uuid_consulta": "nuevo-uuid-unico",
  "url_imagen": "https://url-publica/imagen.jpg"
}
```

### 3. Consultar Resultado

```bash
GET {{base_url}}/api/v1/detecciones/{uuid_consulta}
Headers:
  X-API-Key: {{api_key}}
```

### 4. Listar Todos los Análisis

```bash
GET {{base_url}}/api/v1/detecciones?skip=0&limit=10
Headers:
  X-API-Key: {{api_key}}
```

---

## ❌ Códigos de Error Comunes

| Código | Descripción | Solución |
|---|---|---|
| `400` | Datos inválidos | Verifica que `uuid_consulta` y `url_imagen` sean válidos |
| `401` | No autenticado | Verifica que el header `X-API-Key` sea correcto |
| `404` | No encontrado | Verifica que el UUID o cliente exista |
| `409` | UUID duplicado | El UUID ya fue usado, genera uno nuevo |
| `500` | Error del servidor | Error procesando la imagen (formato, acceso, etc.) |

## 💡 Tips

1. **UUIDs únicos**: Cada `uuid_consulta` debe ser único. Genera un UUID v4 nuevo para cada análisis.
2. **URLs públicas**: Las imágenes deben estar en URLs públicamente accesibles (sin autenticación).
3. **Formatos soportados**: Solo `.jpg`, `.jpeg`, `.png`
4. **API Key segura**: Usa al menos 20 caracteres con letras, números y símbolos.
5. **Paginación**: Usa `skip` y `limit` para manejar grandes volúmenes de resultados.

## 🔗 Ejemplos de Environments

### Producción

```json
{
  "base_url": "http://detection-issue-service.eastus2.cloudapp.azure.com",
  "api_key": "{{TU_API_KEY_REAL}}"
}
```

### Desarrollo Local

```json
{
  "base_url": "http://localhost:5000",
  "api_key": "test-api-key-local"
}
```

## 📞 Soporte

- **Repositorio**: https://github.com/CodAress/infrastructure-issue-detection-service
- **Documentación**: Ver archivo README.md en el repositorio
