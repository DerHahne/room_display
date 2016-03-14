FROM python:2-onbuild

WORKDIR /var/app

CMD chmod +x ./docker_start.sh && ./docker_start.sh
