# MLChallenge

<p align="center"><img width=12.5% src="https://upload.wikimedia.org/wikipedia/en/thumb/2/20/MercadoLibre.svg/1200px-MercadoLibre.svg.png"></p>

## Overview

In this challenge we developed a crawler application which retrieves information about how many times a link was referenced in another page and save this information in a database. After that, we enriched each link with features of themself. With this features, we made a model to predict references of a link and serves this model in a REST API.

## Goals

1. Develop a Crawler that saves link references in a database;
2. Develop an API do get features of links (if the link already exists use it features, else create then);
3. Train a Random Forest that predict link references;
4. Deploy this model and serves with an API.

## Architecture


## Understanding the repository

```
.
+-- .github
|   +-- workflows
|       +-- cicd.yaml: CI/CD pipeline for Github Actions
+-- app
|   +-- batch_event
|       +-- test
|           +-- lambda_test.py: Unit tests of lambda_batch_event.py
|       +-- lambda_batch_event.py: Application that was triggered when put csv file inside the s3 bucket and send the links to SQS
|       +-- requirements.txt: python requirements for this lambda
|   +-- entrypoint
|       +-- test
|           +-- lambda_test.py: Unit tests of lambda_entrypoint.py
|       +-- lambda_entrypoint.py: Application used as backend of API Gateway for get/create features of a link
|       +-- requirements.txt: python requirements for this lambda
|   +-- feature_generation
|       +-- test
|           +-- lambda_test.py: Unit tests of lambda_feature_generation.py
|       +-- lambda_feature_generation.py: Application that generates features and put then into Dynamodb
|       +-- requirements.txt: python requirements for this lambda
|   +-- processing
|       +-- test
|           +-- lambda_test.py: Unit tests of lambda_processing.py
|       +-- lambda_processing.py: Application that find all links referenced in a page and add its to dynamo
|       +-- requirements.txt: python requirements for this lambda
+-- predict
|       +-- test
|           +-- lambda_test.py: Unit tests of lambda_batch_event.py
|       +-- lambda_predict.py: Application used as backend of API Gateway to predict appearances of a link
|       +-- requirements.txt: python requirements for this lambda
+-- dockerfiles
|   +-- lambda_batch_event.dockerfile: Dockerfile with the application that we will deploy in Lambda Container
|   +-- lambda_entrypoint.dockerfile: Dockerfile with the application that we will deploy in Lambda Container
|   +-- lambda_feature_generation.dockerfile: Dockerfile with the application that we will deploy in Lambda Container
|   +-- lambda_processing.dockerfile: Dockerfile with the application that we will deploy in Lambda Container
|   +-- lambda_predict.dockerfile: Dockerfile with the application that we will deploy in Lambda Container
+-- infra
|   +-- infra.yaml: IaaC contaning all resources required for our application
+-- README.md
```

## Configuring in your account

To use this application in your account you should follow the following steps:

1. Fork this repository;
2. Add your AWS credentials in Github Secrets;
3. Make a commit to start the CI CD pipeline;
4. Wait Github actions finish;
5. When all the steps were completed, access your AWS account in **sa-east-1** region;
6. Search for S3 and enters in **crawler-ml-challenge** (or the name you choose, if you change this in infra.yaml);
7. Creates a folder called **inputs/** and upload a csv file with each link you want to start the crawler in one line, e.g:

| https://www.google.com    |
|---------------------------|
| https://www.wikipedia.com |
|                           |




## Future works
