#!/bin/bash

# 🚀 Script de actualización rápida para Azure VM
# Uso: bash update_deployment.sh

set -e  # Salir si hay error

echo "🚀 Iniciando actualización del servicio..."

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: No se encuentra app.py. Ejecuta este script desde el directorio raíz del proyecto.${NC}"
    exit 1
fi

echo -e "${YELLOW}📥 Descargando últimos cambios...${NC}"
git pull origin main

echo -e "${YELLOW}🔍 Verificando dependencias...${NC}"
pip install -r requirements.txt --quiet

echo -e "${YELLOW}🔄 Reiniciando servicio...${NC}"

# Detectar método de ejecución
if command -v systemctl &> /dev/null; then
    # Systemd
    SERVICE_NAME="flask-detection-service"
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${YELLOW}   Usando systemd...${NC}"
        sudo systemctl restart $SERVICE_NAME
        echo -e "${GREEN}✅ Servicio reiniciado con systemd${NC}"
    else
        echo -e "${YELLOW}   Servicio systemd no encontrado, probando PM2...${NC}"
    fi
fi

if command -v pm2 &> /dev/null; then
    # PM2
    if pm2 list | grep -q "detection-service"; then
        echo -e "${YELLOW}   Usando PM2...${NC}"
        pm2 restart detection-service
        echo -e "${GREEN}✅ Servicio reiniciado con PM2${NC}"
    fi
fi

# Si no se encontró systemd ni PM2, dar instrucciones manuales
if ! command -v systemctl &> /dev/null && ! command -v pm2 &> /dev/null; then
    echo -e "${YELLOW}⚠️  No se detectó systemd ni PM2${NC}"
    echo -e "${YELLOW}   Reinicia manualmente el servicio con:${NC}"
    echo -e "${YELLOW}   1. Detén el proceso actual: pkill -f 'python app.py'${NC}"
    echo -e "${YELLOW}   2. Inicia el servicio: python app.py &${NC}"
    echo -e "${YELLOW}   O con gunicorn: gunicorn -w 4 -b 0.0.0.0:80 app:app${NC}"
fi

echo ""
echo -e "${YELLOW}🧪 Verificando servicio...${NC}"

# Esperar 3 segundos para que el servicio arranque
sleep 3

# Verificar endpoint de health
HEALTH_URL="http://localhost/api/v1/health"
echo -e "${YELLOW}   Consultando: $HEALTH_URL${NC}"

if curl -s -f "$HEALTH_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Servicio respondiendo correctamente${NC}"
    
    # Mostrar estado del servicio
    echo ""
    echo -e "${GREEN}📊 Estado del servicio:${NC}"
    curl -s "$HEALTH_URL" | python3 -m json.tool
else
    echo -e "${RED}❌ Error: El servicio no responde en el endpoint de health${NC}"
    echo -e "${RED}   Verifica los logs del servicio${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Actualización completada exitosamente!${NC}"
echo ""
echo -e "${YELLOW}🌐 URLs disponibles:${NC}"
echo -e "   Swagger UI: http://detection-issue-service.eastus2.cloudapp.azure.com/api/v1/docs"
echo -e "   API Spec:   http://detection-issue-service.eastus2.cloudapp.azure.com/api/v1/apispec.json"
echo -e "   Health:     http://detection-issue-service.eastus2.cloudapp.azure.com/api/v1/health"
echo ""
