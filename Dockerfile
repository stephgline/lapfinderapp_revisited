
FROM python:3.6.5-jessie

WORKDIR /pool_app

COPY requirements.txt .

RUN pip3 install -r requirements.txt

#copy all other files
COPY . .

#ENV PORT 5000

#EXPOSE $PORT

#command to launch app
CMD ["/bin/bash", "-c", "python3 runa.py"]
