FROM python:3.9
RUN mkdir /racing-reference
WORKDIR /racing-reference
COPY requirements.txt /requirements.txt
RUN apt-get update && apt-get install -y xvfb
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
COPY . /racing-reference/
CMD [ "python", "main.py"]