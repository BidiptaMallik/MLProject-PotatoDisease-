FROM tensorflow/serving

# COPY ENTIRE MODELS FOLDER
COPY ./models /models

ENV MODEL_NAME=potatoes_model

EXPOSE 8501

CMD tensorflow_model_server \
  --port=8500 \
  --rest_api_port=8501 \
  --model_base_path=/models \
  --model_name=potatoes_model