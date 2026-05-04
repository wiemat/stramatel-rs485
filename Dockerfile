FROM python:3.12
WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./read.py ./read.py

CMD ["python", "-u", "./read.py" ]
