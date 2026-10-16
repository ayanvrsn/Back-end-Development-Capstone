FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput \
    && chgrp -R 0 /app \
    && chmod -R g=u /app
EXPOSE 8000
CMD ["sh", "entrypoint.sh"]
