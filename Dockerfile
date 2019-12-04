FROM python:3.6.5

ENV HOME=/opt/app

ENV RUN_MODE=prod

WORKDIR $HOME

COPY requirements.txt $HOME
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
# for debugging only
# RUN apt install -y nano nmap

COPY . $HOME

EXPOSE 80

ENV PYTHONUNBUFFERED=true

CMD ["/bin/sh", "run-deploy.sh"]
