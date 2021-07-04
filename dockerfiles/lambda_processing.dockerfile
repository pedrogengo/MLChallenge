FROM public.ecr.aws/lambda/python:3.8

# Installing requirements
COPY /app/processing/requirements.txt  .
RUN  pip3 install -r requirements.txt

# Copy function code
COPY /app/processing/lambda_processing.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_processing.handler" ]