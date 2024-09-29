FROM python:3.11.5

# Set the working directory in the container
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev

RUN apt-get install -y poppler-utils libpoppler-cpp-dev
RUN apt-get install -y libgdcm-dev libjpeg-dev


COPY requirements.txt ./
RUN pip install -r requirements.txt
# RUN pip3 install tf-keras==2.16.0

COPY ./scseg ./scseg
COPY ./spinal_cord_api ./spinal_cord_api
COPY ./trained_model ./trained_model
COPY ./api_main.py ./api_main.py
RUN mkdir results


EXPOSE 8000
CMD ["python", "api_main.py" ]  

# #, "--host", "0.0.0.0", "--port", "8888"]