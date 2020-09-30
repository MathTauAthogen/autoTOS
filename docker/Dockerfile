FROM ubuntu:18.04

COPY *.py /app/
COPY outputs /app/outputs

RUN apt-get update -y && \
	apt-get install -y python3-pip python3-dev git

RUN python3 -m pip install --upgrade pip

RUN export LC_ALL=C.UTF-8 && export LANG=C.UTF-8 && \
	pip install spacy && python3 -m spacy download en

RUN pip install --upgrade tensorflow==2.2.0 tensorflow-addons==0.10.0

RUN git clone -b development https://github.com/IndicoDataSolutions/finetune && cd finetune && python3 setup.py develop
RUN pip install tensorflow-gpu --upgrade 

WORKDIR /app

ENTRYPOINT ["python3", "train.py", "outputs/train-filter.json"]