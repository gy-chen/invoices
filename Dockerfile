FROM python:3.7
RUN apt-get update && apt-get install -y libzbar0
ADD . /opt/webapp
WORKDIR /opt/webapp
RUN pip install .
EXPOSE 9090
CMD uwsgi --emperor ./apps