FROM python:3.9.13

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip3 install -U pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=flaskr
# watch app' files
ENV FLASK_DEBUG=True
ENV FLASK_ENV=development

# running Flask as a module
CMD ["sh", "-c", "sleep 5 \ 
    && python -m flask run --host=0.0.0.0"]