from abc import ABC, abstractmethod
import logging
from datetime import datetime
from typing import Dict, Any, List
from pymongo import MongoClient
import os
import json
from threading import Lock
from app.core.config import settings


def create_basic_logger():
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


logger = create_basic_logger()


class BaseDBLogger(ABC):

    def __init__(self) -> None:
        self.log_level = settings.LOG_LEVEL
        self.log_format = settings.LOG_FORMAT
        self.log_dir = settings.LOG_DIR
        self.logger = None

    def _setup_logger(self):
        logger = logging.getLogger(f"{self.model_name}_{self.model_tag}")
        logger.setLevel(self.log_level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(self.log_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @abstractmethod
    def log_operation(self, message: str, level: str = "info", **kwargs):
        pass

    @abstractmethod
    def log_metadata(self, metadata: Dict[str, Any]):
        pass

    @abstractmethod
    def log_model_results(self, results: Dict[str, Any]):
        pass

    @abstractmethod
    def get_prediction(self, prediction_id: str):
        pass

    @abstractmethod
    def get_model_performance(self, start_date: datetime, end_date: datetime):
        pass


class MongoDBLogger(BaseDBLogger):
    def __init__(self, name: str, model_name: str, model_tag: str, *args, **kwargs):
        self.client = MongoClient(settings.MONGODB_URL)

        self.db = self.client[name]
        self.predictions_collection = self.db["predictions"]
        self.logs_collection = self.db["operational_logs"]
        self.metadata_collection = self.db["metadata"]
        self.results_collection = self.db["model_results"]

        logger.info(f"Connected to MongoDB: {self.client.server_info()}")

        self.model_name = model_name
        self.model_tag = model_tag

        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(f"{self.model_name}_{self.model_tag}")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def log_operation(self, message: str, level: str = "info", **kwargs):
        log_entry = {
            "timestamp": datetime.now(),
            "model_name": self.model_name,
            "model_tag": self.model_tag,
            "message": message,
            "level": level,
            **kwargs,
        }
        self.logs_collection.insert_one(log_entry)
        getattr(self.logger, level)(message)

    def log_metadata(self, metadata: Dict[str, Any]):
        metadata_entry = {
            "timestamp": datetime.now(),
            "model_name": self.model_name,
            "model_tag": self.model_tag,
            **metadata,
        }
        self.metadata_collection.insert_one(metadata_entry)
        self.log_operation(f"Metadata logged: {', '.join(metadata.keys())}", "info")

    def log_model_results(self, input_info: Dict[str, Any], results: Dict[str, Any]):
        results_entry = {
            "timestamp": datetime.now(),
            "model_name": self.model_name,
            "model_tag": self.model_tag,
            "input_info": input_info,
            **results,
        }
        self.results_collection.insert_one(results_entry)
        self.log_operation(f"Model results logged: {', '.join(results.keys())}", "info")

    def get_prediction(self, prediction_id: str):
        return self.predictions_collection.find_one({"_id": prediction_id})

    def get_model_performance(self, start_date: datetime, end_date: datetime):
        # pipeline = [
        #     {
        #         "$match": {
        #             "timestamp": {"$gte": start_date, "$lte": end_date},
        #             "model_name": self.model_name,
        #             "model_tag": self.model_tag,
        #         }
        #     },
        #     {
        #         "$group": {
        #             "_id": None,
        #             "total_predictions": {"$sum": 1},
        #             "avg_context_length": {"$avg": {"$strLenCP": "$context"}},
        #             "avg_question_length": {"$avg": {"$strLenCP": "$question"}},
        #         }
        #     },
        # ]
        # result = list(self.predictions_collection.aggregate(pipeline))
        # return result[0] if result else None
        raise NotImplementedError("get_model_performance not implemented yet")

class FileLogger(BaseDBLogger):
    def __init__(self, name: str, model_name: str, model_tag: str, log_dir: str = None, *args, **kwargs):

        super().__init__()
        self.name = name
        self.model_name = model_name
        self.model_tag = model_tag
        self.log_dir = os.path.join(log_dir if log_dir else settings.LOG_DIR, name)

        os.makedirs(self.log_dir, exist_ok=True)

        self.predictions_file = os.path.join(self.log_dir, f"{model_name}_{model_tag}_predictions.jsonl")
        self.logs_file = os.path.join(self.log_dir, f"{model_name}_{model_tag}_operational_logs.jsonl")
        self.metadata_file = os.path.join(self.log_dir, f"{model_name}_{model_tag}_metadata.jsonl")
        self.results_file = os.path.join(self.log_dir, f"{model_name}_{model_tag}_model_results.jsonl")

        self.file_locks = {
            self.predictions_file: Lock(),
            self.logs_file: Lock(),
            self.metadata_file: Lock(),
            self.results_file: Lock(),
        }

        self.logger = self._setup_logger()

    def _write_to_file(self, file_path: str, data: Dict):
        with self.file_locks[file_path]:
            with open(file_path, "a") as f:
                json.dump(data, f)
                f.write("\n")

    def log_operation(self, message: str, level: str = "info", **kwargs):
        log_entry = {
            "timestamp": datetime.now(),
            "model_name": self.model_name,
            "model_tag": self.model_tag,
            "message": message,
            "level": level,
            **kwargs,
        }
        self._write_to_file(self.logs_file, log_entry)
        getattr(self.logger, level)(message)

    def log_metadata(self, metadata: Dict[str, Any]):
        metadata_entry = {
            "timestamp": datetime.now(),
            "model_name": self.model_name,
            "model_tag": self.model_tag,
            **metadata,
        }
        self._write_to_file(self.metadata_file, metadata_entry)
        self.log_operation(f"Metadata logged: {', '.join(metadata.keys())}", "info")

    def log_model_results(self, input_info: Dict[str, Any], results: Dict[str, Any]):
        results_entry = {
            "timestamp": datetime.now(),
            "model_name": self.model_name,
            "model_tag": self.model_tag,
            "input_info": input_info,
            **results,
        }
        self._write_to_file(self.results_file, results_entry)
        self.log_operation(f"Model results logged: {', '.join(results.keys())}", "info")

    def get_prediction(self, prediction_id: str):
        # This method is not efficient for file-based logging and should be implemented differently
        # or considered not supported for file-based logging
        raise NotImplementedError("get_prediction is not efficiently implemented for file-based logging")

    def get_model_performance(self, start_date: datetime, end_date: datetime):
        # This method would require reading and processing all prediction logs
        # It's not efficient for file-based logging and should be implemented differently
        raise NotImplementedError("get_model_performance is not efficiently implemented for file-based logging")


class DBLogger:
    def __init__(self, logger: str, name: str, *args, **kwargs):
        self.logger = logger if logger else settings.LOGGER_HANDLER
        self.db_logger = logger_dict[logger](name=name, *args, **kwargs)

    def log_operation(self, message: str, level: str = "info", **kwargs):
        return self.db_logger.log_operation(message, level, **kwargs)

    def log_metadata(self, metadata: Dict[str, Any]):
        return self.db_logger.log_metadata(metadata)

    def log_model_results(self, input_info: Dict[str, Any], results: Dict[str, Any]):
        return self.db_logger.log_model_results(input_info, results)

    def get_prediction(self, prediction_id: str):
        raise NotImplementedError("Not implemented")
        # return self.db_logger.get_prediction(prediction_id)

    def get_model_performance(self, start_date: datetime, end_date: datetime):
        raise NotImplementedError("Not implemented")
        # return self.db_logger.get_model_performance(start_date, end_date)


logger_dict = {"mongo": MongoDBLogger, "file": FileLogger, "basic": logger}
