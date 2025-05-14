# Use uma imagem base Python oficial
FROM python:3.11-slim

# Defina o diretório de trabalho na imagem
WORKDIR /app

# Instale quaisquer dependências do sistema necessárias (se houver)
# Exemplo: RUN apt-get update && apt-get install -y some-package

# Copie o arquivo de dependências
COPY requirements.txt .

# Instale as dependências do Python
# É uma boa prática não executar como root dentro do container, mas para simplificar:
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o código da aplicação para o diretório de trabalho
COPY . .

# Exponha a porta que a aplicação Flask usa (5000, conforme main.py)
EXPOSE 5000

# Comando para iniciar a aplicação usando Gunicorn (servidor WSGI de produção)
# Certifique-se de que gunicorn está em requirements.txt
# Se não estiver, adicione-o e execute `pip install gunicorn` no seu ambiente local
# e atualize o `requirements.txt` com `pip freeze > requirements.txt` antes de copiar.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.main:app"]
