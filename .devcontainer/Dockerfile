FROM mcr.microsoft.com/devcontainers/python:3.12

# Opcional: instala utilitários úteis
RUN apt-get update && apt-get install -y \
    curl \
    git \
    vim \
    less \
    tree \
    && apt-get clean

# Cria uma pasta padrão para você trabalhar quando abrir o terminal
WORKDIR /workspace

# Garante que o VS Code use o usuário padrão (vscode)
USER vscode