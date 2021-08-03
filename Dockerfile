
# parent image
FROM laudio/pyodbc:1.0.4
FROM python:3.7
FROM ubuntu:18.04
#RUN mkdir /app
WORKDIR /
ADD / .
COPY . /

EXPOSE 1433
# install FreeTDS and dependencies
RUN apt-get update \
    && apt-get install -y gnupg

COPY requirements.txt .

RUN apt-get install python3-pip -y


RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y \
 && apt-get install freetds-dev -y \
 && apt-get install freetds-bin -y \
 && apt-get install -y tdsodbc unixodbc-dev\
 && apt-get install tdsodbc -y \
 && apt-get install --reinstall build-essential -y \
 && apt-get install apt-utils -y \
 && apt-get install gcc

RUN apt-get clean -y

# populate "ocbcinst.ini"
RUN echo "[FreeTDS]\n\
TDS_Version = '7.3'\n\
Description = FreeTDS unixODBC Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

ADD odbcinst.ini /etc/odbcinst.ini

RUN apt-get install --reinstall build-essential -y
RUN apt-get install freetds-common freetds-bin tdsodbc

RUN pip3 install --trusted-host pypi.python.org pyodbc sqlalchemy==1.3.5
RUN pip3 install yarl==1.4.0
RUN pip3 install multidict==4.7.3
RUN pip3 install -r requirements.txt



EXPOSE 5000
EXPOSE 1433
# run app.py upon container launch
CMD ["python3", "-u", "app.py"]
