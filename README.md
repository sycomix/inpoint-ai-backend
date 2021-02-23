# The main back-end application of the inPOINT project.

## Setup for development (tested on Ubuntu)

System Dependencies:
- docker
- docker-compose
- Python 3
- virtualenv

Clone the repository and type the following commands:

```bash
virtualenv env -p python3
source env/bin/activate
cd inpoint-back-end/
pip install -r requirements.txt
```

## Run the application for development

1. Start MongoDB database:
```bash
docker-compose up
```
2. Start API
```bash
./run.sh
```

## Dockerize the application
TODO

## Important

- Before committing your code changes do not forget to run the `format_code.sh` script
- Please try to follow naming conventions and best practices
