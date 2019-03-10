FROM pytorch/pytorch:1.0.1-cuda10.0-cudnn7-devel

RUN python3 -m pip install --upgrade pip \
&& python3 -m pip install jupyter \
&& git clone https://github.com/NVIDIA/apex.git \
&& cd apex \
&& pip install -v --no-cache-dir --global-option="--cpp_ext" --global-option="--cuda_ext" . \
&& pip install scikit-learn pytorch_pretrained_bert seqeval

CMD jupyter notebook --allow-root --ip=0.0.0.0
