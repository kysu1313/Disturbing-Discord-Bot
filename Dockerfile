
# parent image
FROM python:3.9

#RUN mkdir /app
WORKDIR /
ADD / .
COPY . /

EXPOSE 1433
# install FreeTDS and dependencies
RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y \
 && apt-get install freetds-dev -y \
 && apt-get install freetds-bin -y \
 && apt-get install tdsodbc -y \
 && apt-get install --reinstall build-essential -y

# populate "ocbcinst.ini"
RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini
#RUN pip freeze > requirements.txt

# install pyodbc
RUN pip install --trusted-host pypi.python.org pyodbc==4.0.26 sqlalchemy==1.3.5
RUN pip install -r requirements.txt



EXPOSE 5000
# run app.py upon container launch
CMD ["python3", "app.py"]
#CMD tail -f /dev/null


# docker run -it --mount type=bind,source=$PWD,destination=$PWD ghcr.io/quick-lint/quick-lint-js-github-builder:v1
