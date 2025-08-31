import numpy as np
import pandas as pd
import polars as pl


def safe_serialise(obj, max_items=3):
    if isinstance(obj, pd.DataFrame):
        return {
            "type": "DataFrame",
            "shape": obj.shape,
            "columns": list(obj.columns),
            "dtypes": obj.dtypes.astype(str).to_dict(),
            "sample": obj.head(max_items).to_dict(),
        }
    elif isinstance(obj, pd.Series):
        return {
            "type": "Series",
            "shape": obj.shape,
            "name": obj.name,
            "dtype": str(obj.dtype),
            "sample": obj.head(max_items).to_list(),
        }
    elif isinstance(obj, pl.DataFrame):
        return {
            "type": "DataFrame",
            "shape": obj.shape,
            "columns": list(obj.columns),
            "dtypes": {col: str(dtype) for col, dtype in zip(obj.columns, obj.dtypes)},
            "sample": obj.head(max_items).to_dicts(),
        }
    elif isinstance(obj, np.ndarray):
        return {
            "type": "ndarray",
            "shape": obj.shape,
            "dtype": str(obj.dtype),
            "sample": obj.flat[:max_items].tolist(),
        }
    elif isinstance(obj, (list, tuple, set)):
        sample = list(obj)[:max_items]
        return {
            "type": type(obj).__name__,
            "length": len(obj),
            "sample": sample,
        }
    elif isinstance(obj, dict):
        sample_items = list(obj.items())[:max_items]
        return {
            "type": "dict",
            "length": len(obj),
            "sample": dict(sample_items),
        }
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        return str(obj)
