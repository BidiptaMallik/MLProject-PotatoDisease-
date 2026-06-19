FROM tensorflow/serving

COPY ./models/potatoes_model /models/potatoes_model

ENV MODEL_NAME=potatoes_model

EXPOSE 8501

CMD ["tensorflow_model_server", \
     "--port=8500", \
     "--rest_api_port=8501", \
     "--model_name=potatoes_model", \
     "--model_base_path=/models/potatoes_model"]