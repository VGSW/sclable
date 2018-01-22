FROM alpine
LABEL vendor=oftl

RUN apk update \
 && apk upgrade \
 && apk add \
    python3 \
    py3-yaml \
    py3-prompt_toolkit \
    graphviz \
    xdg-utils \
    perl \
    wget \
    make

RUN pip3 install graphviz
RUN wget -O - https://cpanmin.us | perl - App::cpanminus \
 && cpanm Graph::Easy

RUN mkdir /root/coffee
COPY coffee/ /root/coffee/
COPY *.yml /root/

WORKDIR /root/
CMD ["python3", "-m", "coffee"]
