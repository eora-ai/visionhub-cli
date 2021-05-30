import math
from pathlib import Path
from typing import List, Dict, Optional, Union, Any

import cv2
import numpy as np

from melody_mixer import MelodyMixer


# this dictionary will be visible in all the methods of this module
GLOBAL_KEYS = {"fps": None, "is_input_video": False}
MELODY_MIXER = MelodyMixer(
    str(Path(__file__).resolve().parent / Path("./assets/ya_shagayu_po_moskve.mp3"))
)


def init(
    height: int, width: int, fps: int, length: int, audio_fps: Optional[int] = None
):
    """
    Resets the internal state of a stateful model (called in VID2* modes only)
    :param height: height of the input images going to be sent
    :param width: width of the input images going to be sent
    :param fps: frames per second of the input video if the input is video
    :param length: number of frames of the input video if the input is video
    :param audio_fps: audio frequency of the incoming audio stream (in frames per second, e.g. 44100)
    """
    GLOBAL_KEYS["fps"] = fps
    GLOBAL_KEYS["is_input_video"] = True
    video_duration = math.ceil(length / fps)  # in seconds
    MELODY_MIXER.reset(fps, video_duration)


def predict_batch(
    samples: List[Dict[str, Union[np.ndarray, str]]], draw: bool = True
) -> List[Dict[str, Any]]:
    """
    Collects model predictions for batch of samples
    :param samples: list of dicts having structure:
        - image: np.ndarray of shape (H, W, 3) and dtype=np.uint8, order of channels - RGB
        - (Optional) sound: np.ndarray of shape (N, 2) or (N, 1) and dtype=np.float32
        representing one MoviePy audio chunk where N - number of frames in the chunk,
        2 or 1 - number of channels, for stereo and mono respectively
        - meta: serializable dict of parameters required by model
    :param draw: whether to draw resulting images for the given samples (default: True)
    :return: list of dicts having structure:
        - prediction: JSON serializable dict with model output data
        - (Optional) image: result of drawing - np.ndarray of shape (H, W, 3) and dtype=np.uint8,
        order of channels - RGB. This parameter must be specified if draw = True was passed,
        otherwise it should be omitted
        - (Optional) sound: np.ndarray of shape (N, 2) or (N, 1) and dtype=np.float32
        representing one MoviePy audio chunk where N - number of frames in the chunk,
        2 or 1 - number of channels, for stereo and mono respectively.
        If sound isn't going to be changed don't return this key in output result
    """
    results = []

    # iterate over batch
    for sample in samples:
        # read input image parameters
        image = sample["image"]
        h, w = image.shape[:2]
        prediction = {"height": h, "width": w}  # this is our prediction

        # the must have key
        result = {"prediction": prediction}

        # if it was asked to draw the result then do it
        if draw:
            meta = sample.get("meta", {})
            text = meta.get("text", "TEST TEXT")
            image = _draw(image, text, GLOBAL_KEYS["fps"])
            result["image"] = image

        if GLOBAL_KEYS["is_input_video"]:
            result["sound"] = MELODY_MIXER.next_sound_chunk()

        # collect results for batch of samples
        results.append(result)

    return results

def _draw(image: np.ndarray, text: str, fps=None) -> np.ndarray:
    """
    Draws prediction (in this case input meta) on the image
    :param image: np.ndarray of shape (H, W, 3) and dtype=np.uint8, order of channels - RGB
    :param text: text to draw
    :return: np.ndarray of shape (H, W, 3) and dtype=np.uint8, order of channels - RGB
    """
    image = image.copy()

    h, w = image.shape[:2]
    cv2.putText(
        image,
        text,
        (10, int(h - h / 20)),
        cv2.FONT_HERSHEY_PLAIN,
        w // 100,
        (0, 0, 255),
        thickness=w // 100,
    )

    if fps is not None:
        cv2.putText(
            image,
            f"FPS: {fps}",
            (10, int(min(h, w) / 7.2)),
            cv2.FONT_HERSHEY_PLAIN,
            min(h, w) // 90,
            (0, 255, 0),
            thickness=w // 100,
        )

    return image
