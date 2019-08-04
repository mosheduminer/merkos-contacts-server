FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

LABEL maintainer="Moshe Uminer <mosheduminer@gmail.com>" \
					version="1.0"

CMD uvicorn main:app --host 0.0.0.0 --port 80