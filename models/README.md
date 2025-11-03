# Carpeta de Modelos YOLO Entrenados

Esta carpeta contiene el modelo YOLO entrenado para detectar incidencias de infraestructura (baches, basura acumulada, semáforos malogrados, postes caídos).

## 📋 Instrucciones

### 1. **Descargar tu Modelo**

Coloca tu modelo entrenado `best.pt` en esta carpeta:

```
models/
└── best.pt  ← Coloca tu modelo aquí
```

### 2. **Configuración**

El modelo se configura automáticamente desde `.env`:

```env
# En .env
YOLO_MODEL_PATH=./models/best.pt
YOLO_CONF_THRESHOLD=0.30
YOLO_IMGSZ=640
```

### 3. **Verificar Carga**

Cuando inicies la aplicación, verás:

```
✅ 📁 Cargando modelo YOLO desde: ./models/best.pt
✅ 🤖 Modelo YOLO cargado: best.pt
   Clases: {0: 'pothole', ...}
   Umbral: 0.30
```

## 🎯 Características del Modelo

- **Arquitectura**: YOLO11 (o la versión que uses)
- **Clases**: Detección de incidencias de infraestructura
- **Umbral configurable**: Ajustable desde `.env`
- **Input size**: 640x640 (configurable)
- **Output**: Cajas delimitadoras con confianza

## 📊 Rendimiento Esperado

Según tu código de entrenamiento en Colab:

- **mAP50 Box**: ~75.7%
- **mAP50 Mask**: ~76.4%
- **Precisión**: ~76%
- **Clases detectadas**: pothole (bache)

## 🔧 Umbral de Confianza

El modelo usa `YOLO_CONF_THRESHOLD` para filtrar detecciones débiles:

```python
# En detection/infrastructure/services.py
results = self.modelo.predict(
    source=imagen,
    imgsz=640,
    conf=self.conf_threshold,  # ← Configurado desde .env (0.30 por defecto)
    verbose=False
)
```

**Recomendaciones**:
- `0.30` - Más sensible, detecta más (puede haber falsos positivos)
- `0.50` - Balance recomendado
- `0.70` - Más conservador, menos falsos positivos

## ❌ Solución de Problemas

### "Modelo YOLO no encontrado"

```
❌ Error cargando modelo YOLO: [Errno 2] No such file or directory: './models/best.pt'
```

**Solución**: 
1. Verifica que `best.pt` esté en esta carpeta
2. Revisa que `YOLO_MODEL_PATH` en `.env` sea correcto

### "GPU no disponible"

El modelo funcionará en CPU (más lento):
```
⚠️  Usando CPU (más lento)
```

**Para acelerar**: Instala CUDA y PyTorch con soporte GPU

### Inferencia lenta

Si tarda mucho:
- Reduce `YOLO_IMGSZ` a 320 (más rápido, menos preciso)
- Usa GPU si está disponible
- Procesa en lotes

## 📝 Ejemplo de Uso

```python
from detection.infrastructure.services import YoloInferenceService

# Cargar servicio
yolo = YoloInferenceService(
    model_path='./models/best.pt',
    conf_threshold=0.30
)

# Descargar imagen
imagen = yolo.download_image_from_url('https://ejemplo.com/imagen.jpg')

# Ejecutar inferencia
resultado = yolo.infer(imagen)

print(f"Categoría: {resultado['categoria']}")
print(f"Confianza: {resultado['confianza']:.2%}")
print(f"Detecciones: {resultado['num_detecciones']}")
```

## 🚀 Próximos Pasos

1. ✅ Descarga tu modelo `best.pt` del entrenamiento en Colab
2. ✅ Colócalo en esta carpeta: `models/best.pt`
3. ✅ Ajusta `YOLO_CONF_THRESHOLD` en `.env` si es necesario
4. ✅ Inicia la aplicación: `python app.py`

---

**¿Necesitas ayuda?** Consulta `DETECTION_BC.md` para más información.
