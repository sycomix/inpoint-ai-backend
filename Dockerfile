FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
RUN mkdir /downloads
ADD https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin /downloads
COPY . /app
RUN pip install -r requirements.txt