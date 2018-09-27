FROM ccr.ccs.tencentyun.com/shenghuo/python-base

ADD ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /home/app
ADD . /home/app

CMD ["python", "./run.py"]
