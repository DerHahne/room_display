FROM python:3-onbuild

WORKDIR /var/app

EXPOSE 5000

CMD chmod +x ./docker_start.sh && ./docker_start.sh
