# 🚀 Guía de Deployment - Azure VM

## 📋 Requisitos Previos

- Azure VM con Ubuntu 22.04 LTS
- Mínimo 4GB RAM, 2 vCPUs
- 20GB de disco disponible
- Puerto 80 abierto en el firewall

---

## 🔧 Paso 1: Instalar Docker

```bash
# Conectar a tu VM vía SSH
ssh usuario@tu-vm-azure.eastus.cloudapp.azure.com

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
sudo apt install -y docker.io docker-compose

# Iniciar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verificar instalación
docker --version
docker-compose --version

# Agregar usuario al grupo docker (opcional - para no usar sudo)
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar para que tome efecto
```

---

## 📦 Paso 2: Preparar Archivos

```bash
# Crear directorio del proyecto
mkdir -p ~/infrastructure-detection-service
cd ~/infrastructure-detection-service

# Crear directorios para datos persistentes
mkdir -p data logs
```

---

## 📝 Paso 3: Crear Archivos de Configuración

### 3.1 Crear `docker-compose.yml`

```bash
nano docker-compose.yml
```

**Pega el contenido del archivo `docker-compose.yml`** y guarda (Ctrl+O, Enter, Ctrl+X).

### 3.2 Crear `.env`

```bash
nano .env
```

**Pega el contenido del archivo `.env.production`** y edita:

```properties
# IMPORTANTE: Cambia esta URL por la IP/dominio real de tu backend
BACKEND_PRINCIPAL_URL=http://TU_BACKEND_IP:8000

# Opcional: Cambia estas claves secretas en producción
IAM_SECRET_KEY=tu-clave-secreta-aqui-min-32-caracteres
ADMIN_TOKEN=tu-token-admin-secreto-aqui
```

Guarda (Ctrl+O, Enter, Ctrl+X).

---

## 🚀 Paso 4: Desplegar el Servicio

```bash
# Pull de la imagen desde Docker Hub
docker-compose pull

# Iniciar el servicio
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f

# Verificar que el contenedor está corriendo
docker-compose ps
```

**Deberías ver algo como:**

```
NAME                               STATUS        PORTS
infrastructure-detection-service   Up 2 minutes  0.0.0.0:80->5000/tcp
```

---

## ✅ Paso 5: Verificar Funcionamiento

### 5.1 Health Check

```bash
# Desde dentro de la VM
curl http://localhost/api/v1/health

# Desde tu máquina local
curl http://TU_VM_IP/api/v1/health
```

**Respuesta esperada:**

```json
{
  "status": "healthy",
  "timestamp": "2025-11-08T...",
  "services": {
    "database": "ok",
    "yolo_model": "loaded"
  }
}
```

### 5.2 Verificar Logs

```bash
# Logs del servicio
docker-compose logs detection-service

# Logs en tiempo real (salir con Ctrl+C)
docker-compose logs -f detection-service
```

---

## 🔄 Comandos Útiles

### Gestión del Servicio

```bash
# Detener el servicio
docker-compose stop

# Iniciar el servicio
docker-compose start

# Reiniciar el servicio
docker-compose restart

# Detener y eliminar contenedores
docker-compose down

# Ver estado
docker-compose ps

# Ver uso de recursos
docker stats infrastructure-detection-service
```

### Actualizar a Nueva Versión

```bash
# Pull de la última imagen
docker-compose pull

# Recrear contenedor con nueva imagen
docker-compose up -d --force-recreate

# Verificar logs
docker-compose logs -f
```

### Backup de Datos

```bash
# Backup de la base de datos
sudo tar -czf backup-$(date +%Y%m%d).tar.gz data/ logs/

# Restaurar backup
sudo tar -xzf backup-20251108.tar.gz
```

---

## 🔥 Troubleshooting

### El contenedor no inicia

```bash
# Ver logs detallados
docker-compose logs detection-service

# Verificar que el .env existe
ls -la .env

# Verificar variables de entorno
docker-compose config
```

### No responde en el puerto 80

```bash
# Verificar que el puerto está abierto
sudo netstat -tulpn | grep :80

# Verificar firewall de Azure
# Settings → Networking → Add inbound port rule → Port 80
```

### Modelo YOLO no carga

```bash
# Verificar que el modelo está en la imagen
docker exec infrastructure-detection-service ls -lh /app/models/best.pt

# Debería mostrar: -rw-r--r-- ... 53.2M ... best.pt
```

### Alto uso de memoria

```bash
# Ajustar límites en docker-compose.yml
# Editar la sección deploy.resources.limits.memory
nano docker-compose.yml

# Reiniciar
docker-compose restart
```

---

## 🌐 Acceso desde Internet

### Configurar DNS (Opcional)

Si tienes un dominio:

```bash
# Instalar nginx como reverse proxy
sudo apt install -y nginx

# Configurar nginx
sudo nano /etc/nginx/sites-available/detection-service

# Contenido:
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Activar configuración
sudo ln -s /etc/nginx/sites-available/detection-service /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Configurar SSL (HTTPS) con Let's Encrypt

```bash
# Instalar certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d tu-dominio.com

# Renovación automática (ya configurada por certbot)
sudo certbot renew --dry-run
```

---

## 📊 Monitoreo

### Ver métricas en tiempo real

```bash
# CPU, RAM, RED, DISCO
docker stats infrastructure-detection-service
```

### Logs estructurados

```bash
# Últimas 100 líneas
docker-compose logs --tail=100 detection-service

# Filtrar por palabra clave
docker-compose logs detection-service | grep ERROR
```

---

## 🎯 URLs del Servicio

Una vez desplegado, tu servicio estará disponible en:

```
http://TU_VM_IP/api/v1/health          # Health check
http://TU_VM_IP/api/v1/detecciones     # Endpoints principales
http://TU_VM_IP/api/v1/clients/verify  # Verificar credenciales
```

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica la configuración: `docker-compose config`
3. Verifica el health check: `curl http://localhost/api/v1/health`

---

## ✅ Checklist de Deployment

- [ ] VM creada con mínimo 4GB RAM, 2 vCPUs
- [ ] Docker y docker-compose instalados
- [ ] Puerto 80 abierto en firewall de Azure
- [ ] Archivos `docker-compose.yml` y `.env` creados
- [ ] Variable `BACKEND_PRINCIPAL_URL` configurada correctamente
- [ ] Servicio iniciado con `docker-compose up -d`
- [ ] Health check responde correctamente
- [ ] Logs sin errores críticos
- [ ] Backup configurado (opcional)
- [ ] DNS y SSL configurados (opcional)

---

¡Tu servicio está listo para producción! 🎉
