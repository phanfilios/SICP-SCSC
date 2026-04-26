# SCSC - Sistema de Ciberseguridad Cuántica

Sistema experimental de ciberseguridad basado en principios cuánticos, diseñado para operar en un cluster distribuido de 6 computadoras (1 master + 5 workers).

<img width="1739" height="891" alt="image" src="https://github.com/user-attachments/assets/0a737b75-d701-4062-9b9e-b488e1c7d315" />

##  Instalación Rápida

### En el Master (nodo central)

```bash
# 1. Clonar o copiar el proyecto
cd scsc-quantum-security

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env con las IPs de tus nodos
nano .env

# 5. Ejecutar master
python master/app.py

#Other comands

# Prueba rápida del cluster
python -c "from common.config import config; print(config.to_dict())"

# Probar comunicación
python tests/test_cluster.py

Acceder a http://master_ip:8000/metrics para métricas Prometheus


