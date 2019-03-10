FROM pytorch/pytorch:1.0.1-cuda10.0-cudnn7-devel

RUN python3 -m pip install --upgrade pip \
&& python3 -m pip install jupyter

CMD jupyter notebook --allow-root --ip=0.0.0.0
