FROM python:3.11.5

# Set the working directory in the container
RUN mkdir /usr/src/app
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev

RUN apt-get install -y poppler-utils libpoppler-cpp-dev
RUN apt-get install -y libgdcm-dev libjpeg-dev

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.cargo/bin/:$PATH"





# COPY requirements.txt ./
# RUN pip install -r requirements.txt
# # RUN pip3 install tf-keras==2.16.0

COPY ./app ./app
COPY ./config ./config
COPY ./ml ./ml
COPY ./uv.lock ./uv.lock
COPY ./pyproject.toml ./pyproject.toml
COPY ./.python-version ./.python-version
COPY ./.env ./.env
COPY ./run.py ./run.py

RUN uv venv
RUN uv  sync 




# COPY ./spinal_cord_api ./spinal_cord_api
# COPY ./trained_model ./trained_model
# COPY ./api_main.py ./api_main.py
# RUN mkdir results


EXPOSE 8000
#CMD ["uv", "run", "--no-dev","run.py" ]  

CMD ["uv", "run","run.py" ]  

# #, "--host", "0.0.0.0", "--port", "8888"]