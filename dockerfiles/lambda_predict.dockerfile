FROM public.ecr.aws/lambda/python:3.8

# Installing requirements
COPY /app/predict/requirements.txt  .
RUN  pip3 install -r requirements.txt

# Copy function code
COPY /app/predict/lambda_predict.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "lambda_predict.handler" ]