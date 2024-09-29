# spinal-cord-segmenation


## Setup Notes

- sudo apt-get install libgl1  # For Debian/Ubuntu-based systems  
- sudo apt-get install libgdcm-dev libjpeg-dev

## Docker Usage

**build the image**

```bash
docker build -t spinal-cord-app -f docker/Dockerfile .  
``

``bash
docker run -d --name app -p 8000:8000 spinal-cord-app -v re
``  
# or with custom host and port
docker run -d --name face-analysis -p 9000:9000 -e HOST=0.0.0.0 -e PORT=9000 face-analysis-app
``

```bash
#run with compose
 docker-compose  -f docker/docker-compose.yaml up
``
