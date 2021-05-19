# Stub-container for cv-models

Can be used as base for real cv-models' containers

Developer should put into container `model.py` file with:
- `def predict_batch(samples: List[Dict[str, Union[np.ndarray, str]]], draw: bool = True) -> List[Dict[str, Any]]` - 
  the main callback function performing prediction given input images or frames of the video
- [Optional] `init(height: int, width: int, fps: int, length: int, audio_fps: Optional[int] = None)` - 
  callback function for initialization, which provides basic information from the input's metadata
  
For more details look at the `model.py` of this example.
