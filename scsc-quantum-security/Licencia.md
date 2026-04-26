
---

## 🚀 **Instrucciones para desplegar AHORA:**

### En el Master (tu computadora principal):
```bash
# 1. Crear directorio del proyecto
mkdir -p scsc-quantum-security
cd scsc-quantum-security

# 2. Crear todos los archivos que te acabo de dar
# (Copia cada uno con su contenido)

# 3. Configurar .env con las IPs reales
nano .env
# CAMBIAR MASTER_HOST y NODE_X_HOST con las IPs reales

# 4. Instalar y ejecutar
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python master/app.py