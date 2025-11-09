#!/bin/bash
# ==========================================
# Script de Deployment Automático
# Infrastructure Issue Detection Service
# ==========================================

set -e  # Detener si hay errores

echo "🚀 Iniciando deployment del Infrastructure Detection Service..."
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==========================================
# 1. Verificar archivos necesarios
# ==========================================
echo "📋 Verificando archivos..."

if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: docker-compose.yml no encontrado${NC}"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env no encontrado${NC}"
    echo "Copia .env.production a .env y configura las variables"
    exit 1
fi

echo -e "${GREEN}✅ Archivos encontrados${NC}"
echo ""

# ==========================================
# 2. Crear directorios necesarios
# ==========================================
echo "📁 Creando directorios..."
mkdir -p data logs
echo -e "${GREEN}✅ Directorios creados${NC}"
echo ""

# ==========================================
# 3. Pull de la imagen más reciente
# ==========================================
echo "⬇️  Descargando imagen desde Docker Hub..."
docker-compose pull
echo -e "${GREEN}✅ Imagen descargada${NC}"
echo ""

# ==========================================
# 4. Detener servicio anterior (si existe)
# ==========================================
if docker-compose ps | grep -q "Up"; then
    echo "⏸️  Deteniendo servicio anterior..."
    docker-compose down
    echo -e "${GREEN}✅ Servicio detenido${NC}"
    echo ""
fi

# ==========================================
# 5. Iniciar nuevo servicio
# ==========================================
echo "🔄 Iniciando servicio..."
docker-compose up -d
echo -e "${GREEN}✅ Servicio iniciado${NC}"
echo ""

# ==========================================
# 6. Esperar a que el servicio esté listo
# ==========================================
echo "⏳ Esperando a que el servicio esté listo..."
sleep 10

# ==========================================
# 7. Verificar health check
# ==========================================
echo "🏥 Verificando health check..."

MAX_RETRIES=5
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost/api/v1/health > /dev/null; then
        echo -e "${GREEN}✅ Servicio funcionando correctamente${NC}"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo -e "${RED}❌ Error: El servicio no responde después de $MAX_RETRIES intentos${NC}"
            echo ""
            echo "Logs del servicio:"
            docker-compose logs --tail=50 detection-service
            exit 1
        fi
        echo -e "${YELLOW}⏳ Intento $RETRY_COUNT/$MAX_RETRIES - Esperando 5s...${NC}"
        sleep 5
    fi
done

echo ""

# ==========================================
# 8. Mostrar información del servicio
# ==========================================
echo "📊 Estado del servicio:"
docker-compose ps
echo ""

echo "🌐 URLs del servicio:"
echo "  - Health: http://localhost/api/v1/health"
echo "  - API: http://localhost/api/v1/detecciones"
echo ""

echo -e "${GREEN}🎉 ¡Deployment completado exitosamente!${NC}"
echo ""
echo "📝 Comandos útiles:"
echo "  - Ver logs: docker-compose logs -f"
echo "  - Detener: docker-compose stop"
echo "  - Reiniciar: docker-compose restart"
echo "  - Actualizar: ./deploy.sh"
