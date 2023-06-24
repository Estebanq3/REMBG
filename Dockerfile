FROM python:3.10

WORKDIR /fastapi-rembg-app

COPY requirements.txt .

#EXPOSE 8000:8000

RUN pip install -r requirements.txt

COPY ./appv1 ./appv1
COPY ./fotobru-api/web/imgs/FotoBRU/backgrounds ./backgrounds
COPY ./fotobru-api/web/imgs/FotoBRU/tmpcopialocal ./tmp_copia_local


WORKDIR /fastapi-rembg-app/appv1

CMD ["uvicorn","app_API:app", "--host", "0.0.0.0", "--reload"]
