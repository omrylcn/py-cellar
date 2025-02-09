import bentoml
from src.config import load_config, Config
from src.model import Embedder
from typing import List, Dict, Any, Union
import numpy as np


SERVICE_CONFIG = load_config()

@bentoml.service(
    resources={
        "cpu": SERVICE_CONFIG.service.cpu,
        "memory": SERVICE_CONFIG.service.memory,
    },
    traffic={
        "timeout": SERVICE_CONFIG.service.timeout,
        "max_concurrency": SERVICE_CONFIG.service.max_concurrency
    },
    monitoring={"enabled": True},
    health_check={
        "enabled": True,
        "interval": SERVICE_CONFIG.service.interval
    }
)
class Service:
    """
    BentoML service implementation for text embedding generation.

    A service class that provides REST API endpoints for generating text embeddings
    using a pre-trained model. The service configuration is loaded once at module
    level and shared across all instances for consistency and performance.

    Parameters
    ----------
    None

    Attributes
    ----------
    config : Config
        Shared configuration object loaded at module level.
        Contains both model and service parameters.
    model : Embedder
        Initialized text embedding model instance.
        Loaded during service initialization.
    batch_size : int
        Number of sentences to process in each batch.
        Obtained from model configuration.

    See Also
    --------
    Embedder : The underlying model class used for generating embeddings.
    Config : Configuration class that defines service and model parameters.

    Notes
    -----
    All service configuration parameters (CPU, memory, timeouts, etc.) are loaded
    from a YAML configuration file at module initialization. This ensures consistent
    configuration across all service components.

    Examples
    --------
    Starting the service with default configuration:

    >>> service = Service()
    >>> service.get_model_info()
    {'model_type': 'Embedder', 'embedding_dim': 384, ...}

    Making predictions:

    >>> await service.embed_single("Hello world")
    [0.1, 0.2, ..., 0.5]  # Example embedding vector
    """

    def __init__(self):
        """
        Initialize service with pre-loaded configuration.

        The initialization process includes loading the embedding model
        and setting up batch processing parameters. Configuration is shared
        from module level for consistency.

        Notes
        -----
        No parameters are accepted as all configuration is handled through
        the module-level SERVICE_CONFIG object.
        """
        self.config = SERVICE_CONFIG
        
        self.model = Embedder(self.config.model).load()
        self.batch_size = self.config.model.batch_size

    @bentoml.api
    async def embed(self, sentences: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple sentences with batched processing.

        This method processes input sentences in batches to optimize performance
        and resource utilization. The batch size is determined by the model
        configuration.

        Parameters
        ----------
        sentences : List[str]
            A list of input sentences to be embedded.
            Each sentence should be a non-empty string.

        Returns
        -------
        List[float]
            A list of embedding vectors, where each vector is represented as
            a list of floating-point numbers. The length of each vector
            matches the model's embedding dimension.

        See 
        --------
        embed_single : Method for embedding a single sentence.
        
        Notes
        -----
        The method automatically handles batching of inputs. For very large
        inputs, this helps manage memory usage and improve throughput.

        Examples
        --------
        >>> sentences = ["Hello world", "Another example"]
        >>> embeddings = await service.embed(sentences)
        >>> print(len(embeddings))  # Number of input sentences
        2
        >>> print(len(embeddings[0]))  # Embedding dimension
        384  # Example dimension
        """
        embeddings = []
        for i in range(0, len(sentences), self.batch_size):
            batch = sentences[i:i + self.batch_size]
            batch_embeddings = self.model.predict(batch)
            print(batch_embeddings.shape)
            embeddings.extend(batch_embeddings.tolist())
        return embeddings

    @bentoml.api
    async def embed_single(self, sentence: str) -> List[float]:
        """
        Generate embedding for a single sentence.

        A convenience method for generating embeddings when working with
        individual sentences. Internally wraps the sentence in a list
        and uses the same prediction pipeline as batch processing.

        Parameters
        ----------
        sentence : str
            A single input sentence to be embedded.
            Should be a non-empty string.

        Returns
        -------
        List[float]
            The embedding vector for the input sentence, represented as
            a list of floating-point numbers.

        See Also
        --------
        embed : Method for embedding multiple sentences.

        Examples
        --------
        >>> embedding = await service.embed_single("Hello world")
        >>> print(len(embedding))  # Embedding dimension
        384  # Example dimension
        """
        result = self.model.predict([sentence])
        print(result.shape)
        result = result[0]
        print(result.shape)
        return result.tolist()
        
        
    #TODO: add a method to get the model info with fastapi
    @bentoml.api
    def get_model_info(self) -> Dict[str, Any]:
        """
        Retrieve information about the current model and service configuration.

        This method provides a diagnostic view of the service, including
        model type, configurations, and embedding dimensions.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing service information with the following keys:
            - model_type : str
                The class name of the embedding model
            - model_config : Dict
                Current model configuration settings
            - service_config : Dict
                Current service configuration settings
            - embedding_dim : int
                The dimension of the embedding vectors

        Examples
        --------
        >>> info = service.get_model_info()
        >>> print(info['model_type'])
        'Embedder'
        >>> print(info['embedding_dim'])
        384  # Example dimension
        """
        return {
            "model_type": self.model.__class__.__name__,
            "model_config": self.config.model,
            "service_config": self.config.service,
            "embedding_config": self.model.model.model_config
        }