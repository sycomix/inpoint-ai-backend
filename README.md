# The main back-end application of the inPOINT project.

## Setup for development (tested on Ubuntu)

System Dependencies:
- docker
- docker-compose

### Steps
* Install docker (https://docs.docker.com/get-docker/)
* Install docker-compose (https://docs.docker.com/compose/install/)
* Clone the repository
* Copy .env.sample to .env (`cp .env.sample .env`)
* Edit the .env file, if needed
* Start docker

## Running the application for development using Docker
```bash
docker-compose up
```
Check that the back-end application is available at http://localhost:8000

If this is not the case, good luck :-)!

Check the API of the application at http://localhost:8000/docs

## Interacting with MongoDB using MongoDB Compass
Download the MongoDB Compass client to query, create or alter your database.

MongoDB Compass link: https://www.mongodb.com/products/compass

## Important
- Before committing your code changes do not forget to run the `format_code.sh` script
- Please try to follow naming conventions and best practices
