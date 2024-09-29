# spinal-cord-segmenation

- [x] Add evaluation
- [ ] Create more dataset with different resolution and with different ratio
- [x] Add more yolo model with deepth model names
- [x] Add one_ring
- [ ] Add sam
- [ ] Use spinalcordtoolbox to get the ground truth
- [x] Add the data augmentation
- [ ] Analyze model and data
- [ ] Add XAI
- [ ] Calculate real world distance
- [ ] Write api

## Some Important Notes & Links

- <https://github.com/mlyg/DicePlusPlus/tree/main>
- <https://github.com/mlyg/focus-u-net>
- <https://www.springerprofessional.de/en/transunet-with-unified-focal-loss-for-class-imbalanced-semantic-/26549342>
- <https://www.irjet.net/archives/V9/i10/IRJET-V9I10135.pdf>

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
