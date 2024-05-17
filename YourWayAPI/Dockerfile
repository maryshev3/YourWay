FROM --platform=$BUILDPLATFORM python:3.9.9-slim-buster AS builder
EXPOSE 8000
WORKDIR /app 
COPY requirements.txt /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY . /app 
ENTRYPOINT ["python"] 
CMD ["manage.py", "runserver", "0.0.0.0:8000"]

FROM builder as dev-envs
RUN apt-get update && apt-get -y install git

RUN addgroup -system docker && adduser -system --shell /bin/bash --ingroup docker vscode

# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
CMD ["manage.py", "runserver", "0.0.0.0:8000"]