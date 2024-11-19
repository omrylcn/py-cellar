from datetime import timedelta
from feast import FeatureView, Field, ValueType, FileSource, Entity, Project
from feast.types import String, Int64, Float64

project = Project(name="purchase_prediction")

# Define entity
customer = Entity(
    name="customer",
    value_type=ValueType.INT64,
    description="customer id",
)

# Define data sources
batch_source = FileSource(
    path="data/train_features.parquet",  # Will create this from training data
    timestamp_field="event_timestamp",
)

# Define feature view
customer_features = FeatureView(
    name="customer_features",
    ttl=timedelta(days=1),
    entities=[customer],
    schema=[
        Field(name="prev_purchase_amount", dtype=Float64),
        Field(name="days_since_prev_purchase", dtype=Float64),
        Field(name="rolling_mean_prev_amount", dtype=Float64),
    ],
    online=True,
    source=batch_source
)