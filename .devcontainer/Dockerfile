FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

ARG NODE_VERSION=18.16.0

ENV DEBIAN_FRONTEND=noninteractive \
    NVM_DIR=/home/vscode/.nvm

RUN apt update && apt upgrade -y \
    && apt install -y \
        apt-transport-https ca-certificates \
        curl git software-properties-common \
        libgphoto2-dev python3 python3-pip

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
        gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt update \
    && apt install -y docker-ce \
    && usermod -aG docker vscode

USER vscode

RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash \
    && . $NVM_DIR/nvm.sh \
    && nvm install ${NODE_VERSION} \
    && npm i -g yarn
