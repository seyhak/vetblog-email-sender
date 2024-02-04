FROM python3-alpine

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN pip install -r requirements.txt

CMD ["functions-framework-python --target send_mail"]