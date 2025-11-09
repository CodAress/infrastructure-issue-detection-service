# 🚀 Actualización de Deployment - Nuevo DNS

## ✅ Cambios Realizados

### 1. **Swagger/Flasgger Configuration** (`app.py`)
- ✅ Actualizado `host` de `20.109.51.39` a `detection-issue-service.eastus2.cloudapp.azure.com`
- ✅ Corregido error de JavaScript en Swagger (comas finales en diccionarios Python)

### 2. **Swagger Config** (`shared/infrastructure/swagger_config.py`)
- ✅ Eliminadas comas finales en diccionarios (causaban `None is not defined` en JavaScript)
- ✅ Actualizada URL de producción en servers
- ✅ Añadido servidor de producción Azure como primario

### 3. **Postman Collection** (`postman_collection.json`)
- ✅ Actualizada `base_url` de `http://20.109.51.39` a `http://detection-issue-service.eastus2.cloudapp.azure.com`
- ✅ Añadido enlace a Swagger Docs en descripción

### 4. **Postman Guide** (`POSTMAN_GUIDE.md`)
- ✅ Actualizada tabla de variables con nuevo DNS
- ✅ Actualizado environment de producción con nuevo DNS

---

## 🔧 Pasos para Actualizar en Azure VM

### 1. Conectarse a la VM

```bash
ssh usuario@detection-issue-service.eastus2.cloudapp.azure.com
```

### 2. Navegar al directorio del proyecto

```bash
cd /ruta/al/proyecto/infrastructure-issue-detection-service
```

### 3. Hacer pull de los cambios

```bash
git pull origin main
```

### 4. Reiniciar el servicio Flask

Si usas **systemd**:
```bash
sudo systemctl restart flask-detection-service
```

Si usas **PM2**:
```bash
pm2 restart detection-service
```

Si usas **screen/tmux** (manual):
```bash
# Matar proceso anterior
pkill -f "python app.py"

# O encontrar PID y matar
ps aux | grep "python app.py"
kill -9 <PID>

# Iniciar nuevo
python app.py
# O con gunicorn:
gunicorn -w 4 -b 0.0.0.0:80 app:app
```

### 5. Verificar que el servicio está corriendo

```bash
# Verificar logs
tail -f /var/log/flask-detection.log

# O si usas PM2
pm2 logs detection-service

# Verificar puerto
sudo netstat -tulpn | grep :80
```

### 6. Probar los endpoints

```bash
# Health check
curl http://detection-issue-service.eastus2.cloudapp.azure.com/api/v1/health

# Swagger UI
curl -I http://detection-issue-service.eastus2.cloudapp.azure.com/api/v1/docs
```

---

## 🐛 Solución del Error de Swagger

### **Problema:** `Uncaught ReferenceError: None is not defined`

**Causa:** Las comas finales en diccionarios Python se renderizaban como `None` en el JavaScript generado por Flasgger.

**Ejemplo del problema:**
```python
# ❌ Antes (INCORRECTO)
"contact": {
    "name": "API Support",
    "url": "http://localhost:5000",  # ← Coma final
},  # ← Coma final

# ✅ Después (CORRECTO)
"contact": {
    "name": "API Support",
    "url": "http://detection-issue-service.eastus2.cloudapp.azure.com"
}
```

**Archivos corregidos:**
- `shared/infrastructure/swagger_config.py` (3 diccionarios corregidos)

---

## 🌐 URLs Actualizadas

| Servicio | URL Anterior | URL Nueva |
|---|---|---|
| **Base URL** | http://20.109.51.39 | http://detection-issue-service.eastus2.cloudapp.azure.com |
| **Swagger UI** | http://20.109.51.39/api/v1/docs | http://detection-issue-service.eastus2.cloudapp.azure.com/api/v1/docs |
| **API Spec** | http://20.109.51.39/api/v1/apispec.json | http://detection-issue-service.eastus2.cloudapp.azure.com/api/v1/apispec.json |

---

## ✅ Verificación Post-Deployment

1. **Swagger UI carga correctamente:**
   - ✅ No hay errores en consola del navegador
   - ✅ Se muestra la interfaz de Swagger UI
   - ✅ Los endpoints aparecen listados

2. **API funcional:**
   ```bash
   # Verificar credenciales
   curl -X GET "http://detection-issue-service.eastus2.cloudapp.azure.com/api/v1/clients/verify" \
        -H "X-API-Key: tu-api-key"
   ```

3. **Postman actualizado:**
   - ✅ Importar nueva versión de `postman_collection.json`
   - ✅ Verificar que `base_url` apunta al nuevo DNS

---

## 📝 Notas

- El DNS apunta al mismo servidor (IP: 20.109.51.39)
- No se requieren cambios en la configuración de red/firewall
- Los clientes existentes pueden seguir usando la IP o el DNS
- Se recomienda actualizar todos los clientes al DNS para mejor mantenibilidad

## 🔗 Referencias

- **Repositorio:** https://github.com/CodAress/infrastructure-issue-detection-service
- **Documentación Postman:** Ver `POSTMAN_GUIDE.md`
