FROM python:3.7

ARG APP_NAME
ARG APP_PORT
ARG DJANGO_PROJECT
ARG HOST_IP

ENV APP_NAME=${APP_NAME}
ENV DJANGO_PROJECT=${DJANGO_PROJECT}
ENV DJANGO_HOST=$HOST_IP
ENV APP_PORT=$APP_PORT

COPY ./requirements.txt /requirements.txt
COPY ./start.sh /start.sh
RUN pip install -r requirements.txt
EXPOSE 8888
EXPOSE ${APP_PORT}

RUN django-admin startproject ${DJANGO_PROJECT}
COPY ./dev_env/settings_add.py /${DJANGO_PROJECT}/${DJANGO_PROJECT}/settings_add.py
COPY ./dev_env/url_add.py /${DJANGO_PROJECT}/${DJANGO_PROJECT}/url_add.py
ENV DJANGO_SETTINGS_MODULE=${DJANGO_PROJECT}.settings_add

CMD ["bash", "/start.sh"]