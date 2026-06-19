FROM tensorflow/serving

# IMPORTANT: TensorFlow Serving requires version folder "1"
COPY ./models/potatoes_model /models/potatoes_model/1

# Model name (must match backend request URL)
ENV MODEL_NAME=potatoes_model

# Expose REST API port
EXPOSE 8501