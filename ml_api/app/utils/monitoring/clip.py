from prometheus_client import Counter, Histogram, Gauge, Summary

# Model performance metrics
CLIP_REQUESTS_TOTAL = Counter('clip_requests_total', 'Total number of CLIP classification requests')
CLIP_LATENCY = Histogram('clip_latency_seconds', 'Latency of CLIP predictions', buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, float("inf")))
CLIP_CONFIDENCE = Histogram('clip_confidence', 'Confidence scores of CLIP predictions', buckets=(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1))

# Data characteristics metrics
IMAGE_SIZE = Histogram('clip_image_size_bytes', 'Size of input images in bytes', buckets=(0, 10240, 51200, 102400, 512000, 1048576, 5242880, 10485760))  # 0KB to 10MB
IMAGE_DIMENSIONS = Histogram('clip_image_dimensions', 'Dimensions of input images (width * height)', buckets=(0, 65536, 262144, 1048576, 2097152, 8388608))  # 0 to 3840x2160
FILE_EXTENSION = Counter('clip_file_extension', 'File extensions of input images', ['extension'])

# Model behavior metrics
TOP_K_ACCURACY = Histogram('clip_top_k_accuracy', 'Whether the correct label is in the top K predictions', buckets=(1, 3, 5, 10))
LABEL_DISTRIBUTION = Counter('clip_label_distribution', 'Distribution of predicted labels', ['label'])

# Error metrics
CLIP_ERRORS = Counter('clip_errors_total', 'Total number of errors in CLIP process', ['error_type'])

# Resource usage metrics
GPU_MEMORY_USAGE = Gauge('clip_gpu_memory_usage_bytes', 'GPU memory usage for CLIP model')
CPU_USAGE = Gauge('clip_cpu_usage_percent', 'CPU usage percentage for CLIP model')

# Data drift metrics
EMBEDDING_DISTANCE = Gauge('clip_embedding_distance', 'Distance between current image embedding and average embedding')
LABEL_ENTROPY = Gauge('clip_label_entropy', 'Entropy of label distribution over time')

# Batch processing metrics (if applicable)
BATCH_SIZE = Histogram('clip_batch_size', 'Size of batches processed by CLIP', buckets=(1, 2, 4, 8, 16, 32, 64, 128))
IMAGES_PROCESSED = Counter('clip_images_processed_total', 'Total number of images processed by CLIP')