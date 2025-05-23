# Usar imagem base do Python
FROM python:3.11-slim

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos para dentro do container
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expor a porta que o Gunicorn usará
EXPOSE 5000

# Comando para rodar o app com Gunicorn
CMD ["python", "src/main.py"]
