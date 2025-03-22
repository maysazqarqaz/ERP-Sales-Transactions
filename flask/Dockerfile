FROM python:3.12

RUN mkdir /src
WORKDIR /src

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "run:app", "-b", "0.0.0.0:5000"]