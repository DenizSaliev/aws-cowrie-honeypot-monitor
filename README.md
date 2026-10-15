#  AWS Cowrie Honeypot con Alertas en Tiempo Real y Geolocalización en Discord

Despliegue de un sistema de ciberseguridad defensiva y decepción (*honeypot*) en la nube (AWS EC2) utilizando **Cowrie** y Docker. El sistema captura ataques automatizados contra el puerto SSH estándar (22), analiza el tráfico en tiempo real mediante un monitor en Python, geolocaliza el origen de las IPs atacantes y envía alertas instantáneas estructuradas a un canal de Discord.

---

##  Arquitectura del Sistema

<img width="719" height="641" alt="{086FDDF8-D91D-4F35-A82E-BE7CAD92F9C0}" src="https://github.com/user-attachments/assets/fbd96e2e-b783-4d67-a683-33dceb6360a2" />



##  Características Principales

- **Hardening del Host:** Desplazamiento del servicio OpenSSH nativo al puerto `2222` restringido por clave privada, evitando colisiones con el señuelo.
- **Trampa de Decepción SSH:** Exposición del puerto estándar `22` mediante Cowrie en un contenedor aislado de Docker para capturar intentos de escaneo y fuerza bruta.
- **Enriquecimiento de Amenazas (Threat Intel):** Detección automática del país, ciudad y proveedor de Internet (ISP/ASN) de cada atacante.
- **Alertas Automatizadas en Discord:**
  -  Conexiones entrantes con origen geográfico.
  -  Intentos de autenticación con usuario y contraseña probados.
  -  Comandos tecleados por el atacante en la shell emulada (`whoami`, `cat /etc/passwd`, etc.).
- **Persistencia en el Sistema:** Daemonizado mediante un servicio de `systemd` para ejecución continua 24/7.

---

##  Tecnologías Utilizadas

- **Infraestructura:** AWS EC2 (Ubuntu 24.04 LTS)
- **Contenedores:** Docker
- **Honeypot:** Cowrie (Medium-Interaction SSH/Telnet)
- **Scripting & Automatización:** Python 3 (`requests`, `re`)
- **Gestión de Servicios:** Linux `systemd`
- **Notificaciones:** Discord Webhooks

---

##  Pasos de Instalación y Puesta en Marcha

### 1. Modificar el puerto SSH del servidor al 2222

sudo sed -i 's/^#*Port .*/Port 2222/' /etc/ssh/sshd_config
sudo systemctl daemon-reload
sudo systemctl restart ssh

### 2. Desplegar Cowrie en Docker (Puerto 22)
mkdir -p ~/cowrie-data/logs ~/cowrie-data/downloads
sudo chmod -R 777 ~/cowrie-data

sudo docker run -d \
  --name honeypot-cowrie \
  --restart always \
  -p 22:2222 \
  -v /home/ubuntu/cowrie-data/logs:/cowrie/cowrie-data/log \
  -v /home/ubuntu/cowrie-data/downloads:/cowrie/cowrie-data/lib/downloads \
  cowrie/cowrie:latest
### 3. Configurar el Monitor de Alertas en Python

# Crear entorno virtual e instalar dependencias
python3 -m venv ~/alert-env
~/alert-env/bin/pip install -r requirements.txt

# Configurar el servicio systemd
sudo cp honeypot-alert.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now honeypot-alert.service

<img width="486" height="309" alt="image" src="https://github.com/user-attachments/assets/75e95f39-5361-4e01-b34e-1b74371b52fb" />
