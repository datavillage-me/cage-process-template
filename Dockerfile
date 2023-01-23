FROM python:3.10.4-slim-bullseye

#required to install some python dependencies
RUN apt-get update && \
    apt-get install -y wget ca-certificates curl vim git && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /home/user
ENV HOME  /home/user

COPY requirements.txt .
RUN  python -m pip install --upgrade pip && \
     pip install -r requirements.txt && \
     rm -rdf /home/user/.cache/pip

COPY *.py ./

ENTRYPOINT ["python3", "index.py"]
