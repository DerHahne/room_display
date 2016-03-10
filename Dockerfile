FROM python:3-onbuild

WORKDIR /var/app

CMD chmod +x ./docker_start.sh && ./docker_start.sh
