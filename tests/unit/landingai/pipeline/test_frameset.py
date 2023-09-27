import os
from pathlib import Path

from PIL import Image
import pytest

from landingai.common import ObjectDetectionPrediction
from landingai.storage.data_access import fetch_from_uri
from landingai.pipeline.frameset import FrameSet, Frame, PredictionList


def test_save_video(tmp_path: Path):
    frs = FrameSet.from_image("tests/data/images/cereal1.jpeg")

    # Test extension validation
    with pytest.raises(NotImplementedError):
        frs.save_video(str(tmp_path / "video.mp3"))

    filename = str(tmp_path / "video.mp4")
    # Test the combinatorics of fps & video length
    with pytest.raises(ValueError):
        frs.save_video(filename, video_length_sec=2, video_fps=1)

    # Create a 1 frame video with default params
    frs.save_video(filename)
    assert os.path.exists(filename)


def test_predictions_empty():
    frameset = FrameSet.from_image("tests/data/images/cereal1.jpeg")
    assert isinstance(frameset.predictions, list)
    assert isinstance(frameset.predictions, PredictionList)
    assert len(frameset.predictions) == 0


def test_predictions_with_extra_frames_in_frameset(frameset_with_od_coffee_prediction):
    img = Image.open(str(fetch_from_uri("tests/data/images/cereal1.jpeg")))

    other_prediction = ObjectDetectionPrediction(
        score=0.8,
        label_name="coffee",
        label_index=1,
        id="bbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbbb",
        bboxes=(352, 147, 463, 248),
    )
    frame = Frame(image=img, metadata={})
    frame.predictions = [other_prediction]
    frameset_with_od_coffee_prediction.frames.append(frame)

    # Make sure frameset.predictions is a PredictionList that inherits from list
    assert isinstance(frameset_with_od_coffee_prediction.predictions, list)
    assert isinstance(frameset_with_od_coffee_prediction.predictions, PredictionList)

    assert (
        len(frameset_with_od_coffee_prediction.predictions) == 2
    ), "frameset.predictions should concatenate predictions from all frames"
    assert frameset_with_od_coffee_prediction.predictions == [
        frameset_with_od_coffee_prediction.frames[0].predictions[0],
        frameset_with_od_coffee_prediction.frames[1].predictions[0],
    ]


def test_od_predictions_contains_label(frameset_with_od_coffee_prediction):
    assert "coffee" in frameset_with_od_coffee_prediction.predictions
    assert "tea" not in frameset_with_od_coffee_prediction.predictions


def test_od_predictions_filter_threshold(frameset_with_od_coffee_prediction):
    assert "coffee" in frameset_with_od_coffee_prediction.predictions
    assert "tea" not in frameset_with_od_coffee_prediction.predictions

    # "coffee" has a score of 0.6, so this call should filter it out
    filtered_preds = frameset_with_od_coffee_prediction.predictions.filter_threshold(
        0.7
    )
    assert "coffee" not in filtered_preds
    assert "tea" not in filtered_preds


def test_od_predictions_filter_label(frameset_with_od_coffee_prediction):
    assert "coffee" in frameset_with_od_coffee_prediction.predictions
    assert "tea" not in frameset_with_od_coffee_prediction.predictions

    # filter for "coffee" label should keep everything the same
    filtered_preds = frameset_with_od_coffee_prediction.predictions.filter_label(
        "coffee"
    )
    assert "coffee" in filtered_preds
    assert "tea" not in filtered_preds

    # filter for "tea" label should remove "coffee" prediction
    filtered_preds = frameset_with_od_coffee_prediction.predictions.filter_label("tea")
    assert "coffee" not in filtered_preds
    assert "tea" not in filtered_preds


@pytest.fixture
def frameset_with_od_coffee_prediction():
    frameset = FrameSet.from_image("tests/data/images/cereal1.jpeg")
    frameset.frames[0].predictions = [
        ObjectDetectionPrediction(
            score=0.6,
            label_name="coffee",
            label_index=1,
            id="aaaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            bboxes=(352, 147, 463, 248),
        )
    ]
    return frameset
