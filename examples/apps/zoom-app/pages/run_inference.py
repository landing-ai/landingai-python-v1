import numpy as np
import streamlit as st

from sys import platform
from landingai.pipeline.image_source import Webcam
from landingai.predict import Predictor


is_win = platform == "win32"


if "api_key" in st.session_state and "endpoint_id" in st.session_state:
    model = Predictor(
        st.session_state["endpoint_id"], api_key=st.session_state["api_key"]
    )
    # video_src = NetworkedCamera(0, fps=1)
    placeholder = st.empty()

    with Webcam(fps=1) as video_src:
        for frame in video_src:
            frame.run_predict(model).overlay_predictions()
            if len(frame.frames) > 0:
                frame_with_pred = frame.frames[-1].other_images["overlay"]
                placeholder.empty()
                with placeholder.container():
                    st.image(np.array(frame_with_pred))
else:
    st.warning("Please enter your API Key and Endpoint ID in the sidebar.")
