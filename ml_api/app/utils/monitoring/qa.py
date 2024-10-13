from prometheus_client import Counter, Histogram, Gauge,Summary

# Model performance metrics
QA_REQUESTS_TOTAL = Counter('qa_requests_total', 'Total number of QA requests')
QA_LATENCY = Histogram('qa_latency_seconds', 'Latency of QA predictions', buckets=(0.01,0.05,0.1,0.25, 0.5, 1, 2, 5, 10, float("inf")))
QA_CONFIDENCE = Histogram('qa_confidence', 'Confidence scores of QA predictions', buckets=(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1))


# Data characteristics metrics
QUESTION_LENGTH = Histogram('qa_question_length', 'Length of input questions', buckets=(0, 10, 20, 50, 100, 200, 500))
CONTEXT_LENGTH = Histogram('qa_context_length', 'Length of input contexts', buckets=(0, 100, 500, 1000, 2000, 5000, 10000))
ANSWER_LENGTH = Histogram('qa_answer_length', 'Length of generated answers', buckets=(0, 10, 20, 50, 100, 200, 500))

# Model behavior metrics
ANSWER_POSITION = Histogram('qa_answer_position_ratio', 'Relative position of answer in context', buckets=(0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1))
UNANSWERABLE_QUESTIONS = Counter('qa_unanswerable_questions', 'Number of questions with low confidence answers')

# Error metrics
QA_ERRORS = Counter('qa_errors_total', 'Total number of errors in QA process', ['error_type'])