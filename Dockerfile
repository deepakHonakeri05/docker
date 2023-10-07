FROM --platform=linux/amd64 browserless/chrome

USER root

RUN apt-get update
RUN apt-get -y install vim

RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN rm /usr/lib/python3.11/EXTERNALLY-MANAGED

RUN pip3 install requests
RUN pip3 install bs4
RUN pip3 install fastapi uvicorn[standard]
RUN pip3 install webdriver-manager
RUN pip3 install selenium
RUN pip3 install PyVirtualDisplay

WORKDIR /app
COPY ./main.py main.py
COPY ./chromedriver ./chromedriver

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

Expose 8000