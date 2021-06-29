FROM public.ecr.aws/lambda/python:3.8

WORKDIR /app/feature_generation

# Installing requirements
COPY requirements.txt  .
RUN  pip3 install -r requirements.txt

# Copy function code
COPY lambda_feature_generation.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_feature_generation.handler" ]