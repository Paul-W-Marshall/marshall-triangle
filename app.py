"""
Marshall Triangle Visualization Application

Author: Paul W. Marshall
Entity: Fidelitas LLC – Series 1
Year: 2026

License Summary:
- Source code: MIT License (see LICENSE-MIT)
- Generated figures/visual outputs: CC BY-NC 4.0 (see LICENSE-CC-BY-NC-4.0)
- Conceptual framework (Marshall Triangle, sovereign perceptual geometry): 
  All Rights Reserved, governed via Story Protocol
  Minted asset: marshall_triangle-v1-sovereign

Repository: https://github.com/Paul-W-Marshall/marshall-triangle
"""

import streamlit as st
import numpy as np
from harmony_index import HarmonyIndex
import matplotlib.pyplot as plt
from PIL import Image
import io
import base64
import time
from typing import Dict, Optional, List, Any

# Custom CSS for styling sliders
def custom_slider_css():
    return """
    <style>
    /* Custom slider styles for the State & Calibration tab */

    /* Privacy (Red) slider */
    /* Slider track for Privacy */
    div[data-testid="stSlider"]:has(div[aria-valuetext*="privacy_strength"]) div[data-baseweb="slider"] div {
        background-color: #ff5555 !important;
    }
    /* Slider label and value for Privacy */
    div[data-testid="stSlider"]:has(div[aria-valuetext*="privacy_strength"]) {
        color: #ff5555 !important;
    }
    /* Slider value text for Privacy */
    div[data-testid="stSlider"]:has(div[aria-valuetext*="privacy_strength"]) div {
        color: #ff5555 !important;
    }

    /* Performance (Green) slider */
    /* Slider track for Performance */
    div[data-testid="stSlider"]:has(div[aria-valuetext*="performance_strength"]) div[data-baseweb="slider"] div {
        background-color: #55ff55 !important;
    }
    /* Slider label and value for Performance */
    div[data-testid="stSlider"]:has(div[aria-valuetext*="performance_strength"]) {
        color: #55ff55 !important;
    }
    /* Slider value text for Performance */
    div[data-testid="stSlider"]:has(div[aria-valuetext*="performance_strength"]) div {
        color: #55ff55 !important;
    }

    /* Personalization (Blue) slider */
    /* Slider track for Personalization */
    div[data-testid="stSlider"]:has(div[aria-valuetext*="personalization_strength"]) div[data-baseweb="slider"] div {
        background-color: #5555ff !important;
    }
    /* Slider label and value for Personalization */
    div[data-testid="stSlider"]:has(div[aria-valuetext*="personalization_strength"]) {
        color: #5555ff !important;
    }
    /* Slider value text for Personalization */
    div[data-testid="stSlider"]:has(div[aria-valuetext*="personalization_strength"]) div {
        color: #5555ff !important;
    }

    /* Override any default text colors inside sliders */
    div[data-testid="stSlider"] span {
        color: inherit !important;
    }

    /* Force slider thumb to match slider track color */
    div[data-testid="stSlider"] div[data-baseweb="thumb"] div {
        background-color: currentColor !important;
    }
    </style>
    """

# Adaptive sigma calculation for state vector imbalance
def calculate_imbalance_score(r: float, g: float, b: float) -> float:
    """
    Calculate how imbalanced the state vector is using normalized standard deviation.
    Returns 0 for perfectly balanced states, increases toward 1 for extreme imbalance.
    """
    total = r + g + b
    if total == 0:
        return 0.0
    
    r_norm = r / total
    g_norm = g / total
    b_norm = b / total
    
    mean = (r_norm + g_norm + b_norm) / 3.0
    variance = ((r_norm - mean)**2 + (g_norm - mean)**2 + (b_norm - mean)**2) / 3.0
    std_dev = variance ** 0.5
    
    max_std_dev = 0.471
    imbalance = min(1.0, std_dev / max_std_dev)
    return imbalance

def calculate_adaptive_sigma(base_sigma: float, r: float, g: float, b: float) -> tuple:
    """
    Calculate adaptive sigma based on state vector imbalance.
    Returns (adjusted_sigma, imbalance_score, is_compensating)
    """
    imbalance = calculate_imbalance_score(r, g, b)
    compensation_threshold = 0.20
    
    if imbalance <= compensation_threshold:
        return (base_sigma, imbalance, False)
    
    min_compensated_sigma = 0.35
    max_sigma_for_imbalance = 0.48
    
    compensation_factor = (imbalance - compensation_threshold) / (1.0 - compensation_threshold)
    required_sigma = min_compensated_sigma + (max_sigma_for_imbalance - min_compensated_sigma) * compensation_factor
    
    if base_sigma >= required_sigma:
        return (base_sigma, imbalance, False)
    
    return (required_sigma, imbalance, True)

# Session-based state management (ephemeral - no persistence)
def get_calibration() -> Dict[str, float]:
    """Get calibration from session state (ephemeral)"""
    if "calibration" not in st.session_state:
        st.session_state["calibration"] = {"r": 1.0, "g": 1.0, "b": 1.0}
    return st.session_state["calibration"]

def set_calibration(calibration_data: Dict[str, float]) -> bool:
    """Set calibration in session state (ephemeral)"""
    st.session_state["calibration"] = calibration_data
    return True

def get_marshall_states() -> List[Dict]:
    """Get all Marshall states from session state (ephemeral)"""
    if "marshall_states" not in st.session_state:
        st.session_state["marshall_states"] = {}
    return list(st.session_state["marshall_states"].values())

def save_marshall_state(name: str, icon_params: Dict, r_target: float, g_target: float, b_target: float) -> bool:
    """Save a Marshall state to session state (ephemeral)"""
    if "marshall_states" not in st.session_state:
        st.session_state["marshall_states"] = {}
    
    st.session_state["marshall_states"][name] = {
        'name': name,
        'icon_params': icon_params,
        'target': {'r': r_target, 'g': g_target, 'b': b_target}
    }
    return True

def delete_marshall_state(name: str) -> bool:
    """Delete a Marshall state from session state (ephemeral)"""
    if "marshall_states" in st.session_state and name in st.session_state["marshall_states"]:
        del st.session_state["marshall_states"][name]
        return True
    return False

def get_rendering_presets() -> List[Dict]:
    """Get all rendering presets from session state (ephemeral)"""
    if "rendering_presets" not in st.session_state:
        st.session_state["rendering_presets"] = {}
    return [{'name': name, 'params': params} for name, params in st.session_state["rendering_presets"].items()]

def save_rendering_preset(name: str, params: Dict) -> bool:
    """Save a rendering preset to session state (ephemeral)"""
    if "rendering_presets" not in st.session_state:
        st.session_state["rendering_presets"] = {}
    
    st.session_state["rendering_presets"][name] = params
    return True

def delete_rendering_preset(name: str) -> bool:
    """Delete a rendering preset from session state (ephemeral)"""
    if "rendering_presets" in st.session_state and name in st.session_state["rendering_presets"]:
        del st.session_state["rendering_presets"][name]
        return True
    return False

def get_image_base64(harmony_renderer=None, params=None, harmony_state=None, size=100):
    """Generate a base64 encoded image for display in HTML"""
    try:
        if params is None:
            params = {}

        if harmony_state is None:
            harmony_state = {'r': 1.0, 'g': 1.0, 'b': 1.0}

        base_sigma = params.get('sigma', 0.30)
        
        r = harmony_state.get('r', 1.0)
        g = harmony_state.get('g', 1.0)
        b = harmony_state.get('b', 1.0)
        adaptive_sigma, _, _ = calculate_adaptive_sigma(base_sigma, r, g, b)

        small_renderer = HarmonyIndex(
            size=size,
            sigma=adaptive_sigma,
            intensity=params.get('intensity', 1.2),
            edge_blur=params.get('edge_blur', 0.5),
            edge_factor=params.get('edge_factor', 0.5)
        )

        if params and 'calibrated_white_point' in params:
            small_renderer.set_calibration(params['calibrated_white_point'])

        img_bytes = small_renderer.get_image_bytes(
            harmonyState=harmony_state,
            falloff_type=params.get('falloff_type', 'gaussian')
        )

        return base64.b64encode(img_bytes).decode('utf-8')
    except Exception as e:
        st.error(f"Error generating icon: {e}")
        return None

def main():
    if 'layout_preference' not in st.session_state:
        st.session_state.layout_preference = "centered"

    st.set_page_config(
        page_title="Marshall Triangle Visualization",
        page_icon=".streamlit/favicon.png",
        layout=st.session_state.layout_preference
    )

    st.markdown(custom_slider_css(), unsafe_allow_html=True)

    st.title("The Marshall Triangle")

    # Initialize session state variables
    if 'calibration_success' not in st.session_state:
        st.session_state.calibration_success = False
    if 'state_saved' not in st.session_state:
        st.session_state.state_saved = False
    if 'rendering_preset_saved' not in st.session_state:
        st.session_state.rendering_preset_saved = False
    if 'preset_deleted' not in st.session_state:
        st.session_state.preset_deleted = False
    if 'load_rendering_preset' not in st.session_state:
        st.session_state.load_rendering_preset = None
    if 'load_state' not in st.session_state:
        st.session_state.load_state = None
    if 'reset_rendering' not in st.session_state:
        st.session_state.reset_rendering = False
    if 'show_labeled' not in st.session_state:
        st.session_state.show_labeled = False

    # Initialize session state for rendering parameters if not present
    if 'size' not in st.session_state:
        st.session_state.size = 500
    if 'falloff_type' not in st.session_state:
        st.session_state.falloff_type = 'gaussian'
    if 'sigma' not in st.session_state:
        st.session_state.sigma = 0.30
    if 'intensity' not in st.session_state:
        st.session_state.intensity = 1.0
    if 'edge_blur' not in st.session_state:
        st.session_state.edge_blur = 0.5
    if 'edge_factor' not in st.session_state:
        st.session_state.edge_factor = 0.5

    # Initialize session state for Marshall state vector if not present
    if 'privacy_strength' not in st.session_state:
        st.session_state.privacy_strength = 1.0
    if 'performance_strength' not in st.session_state:
        st.session_state.performance_strength = 1.0
    if 'personalization_strength' not in st.session_state:
        st.session_state.personalization_strength = 1.0

    # Get ephemeral calibration from session state
    calibrated_white_point = get_calibration()

    # Handle preset loading and resets
    if st.session_state.reset_rendering:
        st.session_state.size = 1000
        st.session_state.falloff_type = 'gaussian'
        st.session_state.sigma = 0.30
        st.session_state.intensity = 1.0
        st.session_state.edge_blur = 0.5
        st.session_state.edge_factor = 0.5
        st.session_state.reset_rendering = False

    if st.session_state.load_rendering_preset is not None:
        params = st.session_state.load_rendering_preset
        st.session_state.size = params.get('size', 500)
        st.session_state.falloff_type = params.get('falloff_type', 'gaussian')
        if params.get('falloff_type', 'gaussian') == 'gaussian':
            st.session_state.sigma = params.get('sigma', 0.30)
        st.session_state.intensity = params.get('intensity', 1.0)
        st.session_state.edge_blur = params.get('edge_blur', 0.5)
        st.session_state.edge_factor = params.get('edge_factor', 0.5)
        st.session_state.load_rendering_preset = None

    if st.session_state.load_state is not None:
        harmony_state = st.session_state.load_state
        st.session_state.privacy_strength = harmony_state.get('r', 1.0)
        st.session_state.performance_strength = harmony_state.get('g', 1.0)
        st.session_state.personalization_strength = harmony_state.get('b', 1.0)
        st.session_state.load_state = None

    st.markdown("""
    A novel conceptual framework for visualizing triadic balance through color harmony. The Marshall Triangle 
    represents the dynamic equilibrium between **Privacy**, **Performance**, and **Personalization**, using a
    geometric configuration with color sources at midpoints rather than vertices.
    """)

    marshall_state = {
        'r': st.session_state.privacy_strength,
        'g': st.session_state.performance_strength,
        'b': st.session_state.personalization_strength
    }

    size = st.session_state.size
    base_sigma = st.session_state.sigma
    intensity = st.session_state.intensity
    edge_blur = st.session_state.edge_blur
    edge_factor = st.session_state.edge_factor
    falloff_type = st.session_state.falloff_type

    adaptive_sigma, imbalance_score, is_compensating = calculate_adaptive_sigma(
        base_sigma,
        marshall_state['r'],
        marshall_state['g'],
        marshall_state['b']
    )
    
    sigma = adaptive_sigma

    if st.session_state.calibration_success:
        st.success("Calibration applied! The visualization now treats your selected state as the balanced reference point.")
        st.session_state.calibration_success = False

    if is_compensating:
        st.warning(f"Adaptive sigma active: {base_sigma:.2f} → {sigma:.2f} (imbalance: {imbalance_score*100:.1f}%)")

    harmony = HarmonyIndex(
        size=size,
        sigma=sigma,
        intensity=intensity,
        edge_blur=edge_blur,
        edge_factor=edge_factor
    )

    harmony.set_calibration(calibrated_white_point)

    col1, col2 = st.columns([3, 2])

    with col1:
        show_labeled = st.checkbox("Show Labels", value=st.session_state.show_labeled, key="show_labeled")
        
        if show_labeled:
            fig = harmony.plot_with_labels(harmonyState=marshall_state, falloff_type=falloff_type)
            st.pyplot(fig)
            plt.close(fig)
        else:
            img = harmony.render(harmonyState=marshall_state, falloff_type=falloff_type)
            st.image(img, width="stretch")

    with col2:
        st.subheader("Current Marshall State")
        st.markdown(f"""
        - **Privacy (Red)**: {marshall_state['r']:.2f}
        - **Performance (Green)**: {marshall_state['g']:.2f}
        - **Personalization (Blue)**: {marshall_state['b']:.2f}
        """)
        
        st.subheader("White Point Calibration")
        st.markdown(f"""
        - Privacy: {calibrated_white_point['r']:.2f}
        - Performance: {calibrated_white_point['g']:.2f}
        - Personalization: {calibrated_white_point['b']:.2f}
        """)

        buf = io.BytesIO()
        img_export = harmony.render(harmonyState=marshall_state, falloff_type=falloff_type)
        img_export.save(buf, format='PNG')
        st.download_button(
            label="Download Marshall Triangle",
            data=buf.getvalue(),
            file_name=f"marshall_triangle_{int(time.time())}.png",
            mime="image/png"
        )

    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "About the Marshall Triangle", 
        "State & Calibration", 
        "Visualization Settings"
    ])

    # Tab 1: About
    with tab1:
        st.header("About the Marshall Triangle")
        
        st.subheader("The Triadic Framework")
        st.markdown("""
        The Marshall Triangle positions three competing concerns as **midpoint sources** along the edges of an equilateral triangle:
        
        - **Privacy (Red)** — User data protection and anonymity
        - **Performance (Green)** — System speed and efficiency  
        - **Personalization (Blue)** — Tailored user experiences
        
        Secondary colors (Yellow, Cyan, Magenta) emerge at the triangle **vertices** through additive color mixing, 
        while the **convergent white equilibrium point** manifests at the geometric center when all three concerns are balanced.
        """)
        
        st.subheader("The Convergent White Equilibrium Point")
        st.markdown("""
        The most significant conceptual feature is the dynamic White Point:
        
        - Beyond fixed reference systems, the white point in the Marshall Triangle is subjective and user-defined
        - Using the **Triadic Calibration** feature, you can define any state as your preferred balance point
        - This makes the framework adaptable to different contexts and priorities
        """)

    # Tab 2: State & Calibration
    with tab2:
        st.header("Marshall State & Calibration")

        st.subheader("State Vector")
        st.markdown("Adjust the strength of each concern to explore the triadic balance:")

        privacy_strength = st.slider(
            "Privacy (Red)", 
            min_value=0.0, 
            max_value=1.0,
            key="privacy_strength",
            step=0.01
        )

        performance_strength = st.slider(
            "Performance (Green)", 
            min_value=0.0, 
            max_value=1.0,
            key="performance_strength",
            step=0.01
        )

        personalization_strength = st.slider(
            "Personalization (Blue)", 
            min_value=0.0, 
            max_value=1.0,
            key="personalization_strength",
            step=0.01
        )

        marshall_state = {
            'r': privacy_strength,
            'g': performance_strength,
            'b': personalization_strength
        }

        st.subheader("Triadic Calibration")
        st.markdown("""
        Set your current state as your preferred "White Point of Harmony". 
        This personalizes the visualization so your chosen balance appears as white at center.
        
        **Note:** Calibration is session-based and will reset when you reload the page.
        """)

        st.markdown(f"""
        **Current White Point Calibration:**
        - Privacy (Red): {calibrated_white_point['r']:.2f}
        - Performance (Green): {calibrated_white_point['g']:.2f}
        - Personalization (Blue): {calibrated_white_point['b']:.2f}
        """)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Calibrate: Set Current State as White Point"):
                set_calibration(marshall_state)
                st.session_state.calibration_success = True
                st.rerun()

        with col2:
            if st.button("Reset Calibration"):
                set_calibration({'r': 1.0, 'g': 1.0, 'b': 1.0})
                st.success("Calibration reset to default balanced state (1.0, 1.0, 1.0).")
                st.rerun()

        st.subheader("Save Current Marshall State")
        state_name = st.text_input("State Name", value="", key="state_name_input")

        if st.button("Save Current State", key="save_marshall_state_btn"):
            if state_name:
                icon_params = {
                    'size': 100,
                    'sigma': sigma,
                    'intensity': intensity,
                    'edge_blur': edge_blur,
                    'edge_factor': edge_factor,
                    'falloff_type': falloff_type,
                    'calibrated_white_point': calibrated_white_point
                }
                save_marshall_state(
                    state_name, 
                    icon_params, 
                    marshall_state['r'], 
                    marshall_state['g'], 
                    marshall_state['b']
                )
                st.success(f"Marshall State '{state_name}' saved to this session!")
                st.rerun()
            else:
                st.warning("Please enter a name for the state.")

        st.subheader("Saved Marshall States")
        st.info("States are saved to your current session only. They will be cleared when you reload the page.")
        
        marshall_states = get_marshall_states()

        if marshall_states:
            num_cols = 3
            rows = [marshall_states[i:i+num_cols] for i in range(0, len(marshall_states), num_cols)]

            for row in rows:
                cols = st.columns(num_cols)

                for i, state in enumerate(row):
                    with cols[i]:
                        icon_base64 = get_image_base64(
                            None,
                            state['icon_params'],
                            harmony_state={'r': state['target']['r'], 
                                          'g': state['target']['g'], 
                                          'b': state['target']['b']},
                            size=100
                        )

                        if icon_base64:
                            st.markdown(
                                f"<div style='text-align: center;'><img src='data:image/png;base64,{icon_base64}' width='100px'/><br/><b>{state['name']}</b></div>", 
                                unsafe_allow_html=True
                            )

                            st.markdown(
                                f"Pr: {state['target']['r']:.2f}, "
                                f"Pf: {state['target']['g']:.2f}, "
                                f"Ps: {state['target']['b']:.2f}"
                            )

                            if st.button("Load", key=f"load_state_{state['name']}"):
                                st.session_state.load_state = state['target']
                                st.rerun()

                            if st.button("Delete", key=f"delete_state_{state['name']}"):
                                delete_marshall_state(state['name'])
                                st.rerun()
        else:
            st.info("No Marshall states saved yet. Create one by setting your preferred state and clicking 'Save Current State'.")

    # Tab 3: Visualization Settings
    with tab3:
        st.header("Visualization Settings")

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Basic Parameters")

            size = st.slider("Image Size (pixels)", 
                             min_value=500, 
                             max_value=2000, 
                             key="size",
                             step=100)

            falloff_type = st.radio("Falloff Function", 
                                   ["gaussian", "inverse_square"],
                                   index=0 if st.session_state.falloff_type == 'gaussian' else 1,
                                   key="falloff_type")

            if falloff_type == "gaussian":
                sigma = st.slider("Sigma (Gaussian falloff)", 
                                 min_value=0.05, 
                                 max_value=0.5, 
                                 key="sigma",
                                 step=0.01)
            else:
                sigma = 0.2

            intensity = st.slider("Color Intensity", 
                                 min_value=0.1, 
                                 max_value=5.0, 
                                 key="intensity",
                                 step=0.1)

            st.subheader("Advanced Edge Smoothing")

            edge_blur = st.slider("Edge Blur Radius", 
                                min_value=0.0, 
                                max_value=2.0, 
                                key="edge_blur",
                                step=0.1)

            edge_factor = st.slider("Edge Intensity Factor", 
                                    min_value=0.0, 
                                    max_value=1.0, 
                                    key="edge_factor",
                                    step=0.1)

        with col2:
            st.subheader("Save Rendering Presets")
            st.info("Presets are saved to your current session only.")

            preset_name = st.text_input("Preset Name", value="", key="preset_name_input")

            if st.button("Save Current Settings", key="save_rendering_preset_btn"):
                if preset_name:
                    params = {
                        'size': size,
                        'falloff_type': falloff_type,
                        'sigma': sigma,
                        'intensity': intensity,
                        'edge_blur': edge_blur,
                        'edge_factor': edge_factor
                    }
                    save_rendering_preset(preset_name, params)
                    st.success(f"Rendering preset '{preset_name}' saved to this session!")
                    st.rerun()
                else:
                    st.warning("Please enter a name for the preset.")

            if st.button("Reset to Default Settings"):
                st.session_state.reset_rendering = True
                st.rerun()

        st.subheader("Saved Rendering Presets")

        presets = get_rendering_presets()

        if presets:
            num_cols = 3
            rows = [presets[i:i+num_cols] for i in range(0, len(presets), num_cols)]

            for row in rows:
                cols = st.columns(num_cols)

                for i, preset in enumerate(row):
                    if i < len(row):
                        with cols[i]:
                            icon_base64 = get_image_base64(
                                None, 
                                preset['params'], 
                                marshall_state, 
                                size=100
                            )

                            if icon_base64:
                                st.markdown(
                                    f"<div style='text-align: center;'><img src='data:image/png;base64,{icon_base64}' width='100px'/><br/><b>{preset['name']}</b></div>", 
                                    unsafe_allow_html=True
                                )

                                st.markdown(
                                    f"Size: {preset['params'].get('size', 500)}<br/>"
                                    f"Falloff: {preset['params'].get('falloff_type', 'gaussian')}<br/>"
                                    f"Intensity: {preset['params'].get('intensity', 1.0)}"
                                    , unsafe_allow_html=True
                                )

                                if st.button("Load", key=f"load_preset_{preset['name']}"):
                                    st.session_state.load_rendering_preset = preset['params']
                                    st.rerun()

                                if st.button("Delete", key=f"delete_preset_{preset['name']}"):
                                    delete_rendering_preset(preset['name'])
                                    st.rerun()
        else:
            st.info("No rendering presets saved yet. Configure your preferred visual settings and click 'Save Current Settings'.")

    # Attribution Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; font-size: 0.85em; padding: 1rem 0;">
        <strong>Marshall Triangle</strong><br/>
        &copy; 2026 Fidelitas LLC – Series 1 | Author: Paul W. Marshall<br/>
        <a href="https://github.com/Paul-W-Marshall/marshall-triangle" target="_blank" style="color: #888;">GitHub Repository</a><br/>
        <span style="font-size: 0.8em;">
            Code: MIT | Figures: CC BY-NC 4.0 | Conceptual Framework: All Rights Reserved
        </span>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
