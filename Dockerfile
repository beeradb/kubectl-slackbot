FROM ubuntu:16.04

ENV KUBECTL_VERSION v1.2.1
ENV KUBECTL_SHA256 a41b9543ddef1f64078716075311c44c6e1d02c67301c0937a658cef37923bbb

ADD https://storage.googleapis.com/kubernetes-release/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl /bin/kubectl

RUN apt-get -y update \
  && apt-get -y upgrade \
  && apt-get -y install python \
  && apt-get -y install software-properties-common \
  && apt-get clean \
  && echo "${KUBECTL_SHA256} */bin/kubectl" | sha256sum -c - \
  && chmod ugo+x /bin/kubectl

COPY files /
RUN pip install -r /requirements.txt

WORKDIR /app

ENTRYPOINT ["python", "bot.py"]
