FROM python:3.11-slim
WORKDIR /app

# 安裝必要套件
COPY app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 將程式碼與範本 env 複製到容器
COPY app/ ./app
COPY config.env ./config.env
COPY telegram.env ./telegram.env
COPY account.env ./account.env

WORKDIR /app
CMD ["python", "main.py"]
