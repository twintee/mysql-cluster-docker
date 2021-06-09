FROM mysql:8.0

COPY ./.bashrc /root

# aptパッケージインストール
RUN apt-get update && \
    apt-get install -y \
    vim \
    software-properties-common \
    python3 \
    python3-pip \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# pip3 モジュールインストール
RUN pip3 --no-cache-dir install \
    python-dotenv

EXPOSE 3306