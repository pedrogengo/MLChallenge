<p align="center"><img width=12.5% src="https://upload.wikimedia.org/wikipedia/en/thumb/2/20/MercadoLibre.svg/1200px-MercadoLibre.svg.png"></p>

# MLChallenge

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

## Assumptions

- The depth of crawler search was defined as 5. You can change this at infra.yaml (inside the BatchEvent Resource);
- I used only a few link to create the database because I don't want to be charged by AWS and DynamoDB has a limit of throughput of 5 in the free-tier (for read and write);

## Configuring in your account

To use this application in your account you should follow the following steps:

1. Fork this repository;
2. Add your AWS credentials in Github Secrets ([How to get AWS Credentials](https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#email-and-password-for-your-account) and [How to add Github Secrets](https://docs.github.com/en/actions/reference/encrypted-secrets#creating-encrypted-secrets-for-a-repository));
3. Change the nome of the two buckets in infra.yaml for unique names (try to put an identifier after the proposed name like: crawler-bucket-model-<'yourname'>);
4. Make a commit to start the CI CD pipeline;
5. Wait Github actions finish;
6. When all the steps were completed, access your AWS account in **sa-east-1** region;
7. (OPTIONAL) Search for S3 and enters in **crawler-ml-challenge** (or the name you choose, if you change this in infra.yaml);
8. (OPTIONAL) Creates a folder called **inputs/** and upload a csv file with each link you want to start the crawler in one line, e.g:

<center>

|   |
|---|
| https://www.google.com    |
| https://www.wikipedia.com |

</center>

9. (OPTIONAL) This upload will start the crawling process. You can follow the progress at SQS, looking at **Messages available** option in the menu of your queue. When it decreases to zero, it means that crawler process finished;
10. To uses the predict route of API Gateway, you need to search again for S3 and enters in **bucket-model**;
11. Download the model here and upload it to the bucket;
12. Go to the **crawler-predict-appearances Lambda** and change de enviroment variable **MODEL_NAME** to the model that you uploaded in S3;
13. Finished! Now you can use the API!

## Future works

All this work was developed with free-tiers components in order to reduce costs. For future works we can do:

1. Change DynamoDB ProvisionedThroughput for PAY_PER_REQUEST, in other to scales our application;
2. Create the buckets in another repository, in order to don't have problems when we need to delete the stack;
3. Create CI steps to test the integration between components, not only unit tests.