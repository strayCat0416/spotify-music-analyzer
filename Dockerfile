FROM public.ecr.aws/lambda/python:3.10

WORKDIR /var/task

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY index.py .
COPY create_artist_analysis_service.py .
COPY common/ common/

CMD ["index.handler"]
