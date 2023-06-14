FROM python:3.10

WORKDIR /fastapi-rembg-app

COPY requirements.txt .

#EXPOSE 8000:8000

RUN pip install -r requirements.txt

COPY ./app ./app
COPY ./backgrounds ./backgrounds
COPY ./tmp_copia_local ./tmp_copia_local
COPY ./tmp_copia_automatica ./tmp_copia_automatica

WORKDIR /fastapi-rembg-app/app

CMD ["uvicorn","app_API:app", "--host", "0.0.0.0", "--reload"]
