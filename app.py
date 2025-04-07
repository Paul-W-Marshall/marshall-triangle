import streamlit as st
import numpy as np
from harmony_index import HarmonyIndex
import matplotlib.pyplot as plt
from PIL import Image
import io
import json
import os
import sqlite3
import base64
import time
import tempfile
import shutil
from typing import Dict, Optional, List, Any
from refresh_trigger import (
    init_refresh_file, 
    get_refresh_data,
    trigger_refresh,
    record_saved_state,
    record_saved_preset,
    get_saved_states,
    get_saved_presets, 
    delete_saved_state,
    delete_saved_preset
)

# Initialize the refresh trigger file
init_refresh_file()

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

# Database setup and management functions
def init_db():
    """Initialize the database with necessary tables if they don't exist"""
    try:
        conn = sqlite3.connect('harmony_presets.db')
        cursor = conn.cursor()

        print("Initializing database tables...")

        # Create marshall_states table (renamed from harmony_states)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS marshall_states (
            name TEXT PRIMARY KEY,
            icon_params TEXT,
            r_target REAL,
            g_target REAL,
            b_target REAL
        )
        ''')

        # Create rendering_presets table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rendering_presets (
            name TEXT PRIMARY KEY,
            params TEXT
        )
        ''')

        # Keep backward compatibility with old tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS harmony_states (
            name TEXT PRIMARY KEY,
            icon_params TEXT,
            r_target REAL,
            g_target REAL,
            b_target REAL
        )
        ''')

        # Check if old harmony_states table has data to migrate
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='harmony_states'")
        if cursor.fetchone():
            cursor.execute("SELECT COUNT(*) FROM harmony_states")
            harmony_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM marshall_states")
            marshall_count = cursor.fetchone()[0]

            print(f"Found {harmony_count} harmony states and {marshall_count} marshall states")

            # If harmony_states has data but marshall_states is empty, migrate the data
            if harmony_count > 0 and marshall_count == 0:
                print(f"Migrating {harmony_count} states from harmony_states to marshall_states...")
                cursor.execute("INSERT OR IGNORE INTO marshall_states SELECT * FROM harmony_states")
                conn.commit()
                print(f"Migration complete")

        # Verify tables and count entries
        cursor.execute("SELECT COUNT(*) FROM marshall_states")
        marshall_count = cursor.fetchone()[0]
        print(f"Marshall states table contains {marshall_count} entries")

        cursor.execute("SELECT COUNT(*) FROM rendering_presets")
        presets_count = cursor.fetchone()[0]
        print(f"Rendering presets table contains {presets_count} entries")

        conn.commit()
        conn.close()
    except Exception as e:
        error_msg = f"Error initializing database: {e}"
        print(error_msg)
        st.error(error_msg)

def save_marshall_state(name, icon_params, r_target, g_target, b_target):
    """Save a Marshall state preset to the database and refresh file"""
    # First generate a unique ID for this save operation
    operation_id = f"save_{int(time.time() * 1000)}"
    success = False

    try:
        print(f"[{operation_id}] SAVING MARSHALL STATE: name={name}, r={r_target}, g={g_target}, b={b_target}")

        # Convert icon params to JSON for database storage
        icon_params_json = json.dumps(icon_params)

        # APPROACH 1: Save to database with direct connection and parameterized query
        try:
            conn = sqlite3.connect('harmony_presets.db')
            cursor = conn.cursor()

            # First ensure the table exists
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS marshall_states (
                name TEXT PRIMARY KEY,
                icon_params TEXT,
                r_target REAL,
                g_target REAL,
                b_target REAL
            )
            ''')

            # Use parameterized query for safety
            cursor.execute(
                "INSERT OR REPLACE INTO marshall_states (name, icon_params, r_target, g_target, b_target) VALUES (?, ?, ?, ?, ?)",
                (name, icon_params_json, r_target, g_target, b_target)
            )

            # Commit and close
            conn.commit()
            conn.close()
            success = True
            print(f"[{operation_id}] DATABASE SAVE COMPLETED")
        except Exception as e_db:
            print(f"[{operation_id}] DATABASE SAVE FAILED: {e_db}")

        # APPROACH 2: ALWAYS save to refresh trigger file
        try:
            # Record in the refresh trigger file
            refresh_timestamp = record_saved_state(name, icon_params, r_target, g_target, b_target)

            # Set the force refresh flag in session state
            st.session_state.force_hard_refresh = refresh_timestamp

            print(f"[{operation_id}] REFRESH FILE SAVE COMPLETED, timestamp: {refresh_timestamp}")
            success = True
        except Exception as e_file:
            print(f"[{operation_id}] REFRESH FILE SAVE FAILED: {e_file}")

        # If at least one approach succeeded
        if success:
            print(f"[{operation_id}] STATE SAVE SUCCESSFUL")
            return True
        else:
            raise Exception("All save methods failed")

    except Exception as e:
        error_msg = f"Error saving Marshall state: {e}"
        print(f"[{operation_id}] CRITICAL ERROR: {error_msg}")
        import traceback
        print(traceback.format_exc())
        st.error(error_msg)
        return False

def get_marshall_states():
    """Get all saved Marshall states directly from database"""
    # Generate a completely unique timestamp for this fetch
    fetch_timestamp = int(time.time() * 1000000)
    print(f"[{fetch_timestamp}] FETCHING Marshall states DIRECTLY FROM DATABASE...")

    # SIMPLIFIED APPROACH: Get states directly from the database every time
    states = []

    try:
        # Direct database connection with fresh query
        conn = sqlite3.connect('harmony_presets.db')
        cursor = conn.cursor()

        # Query with unique fetch ID in comment to prevent caching
        cursor.execute(f"SELECT name, icon_params, r_target, g_target, b_target FROM marshall_states /* direct_fetch_{fetch_timestamp} */")
        rows = cursor.fetchall()

        # Process results
        for row in rows:
            name, icon_params, r, g, b = row
            try:
                # Parse JSON for icon parameters
                parsed_params = json.loads(icon_params) if icon_params and icon_params.strip() else {}

                # Add to results
                states.append({
                    'name': name,
                    'icon_params': parsed_params,
                    'target': {'r': r, 'g': g, 'b': b}
                })
            except Exception as e:
                print(f"[{fetch_timestamp}] ERROR parsing icon_params for {name}: {e}")
                # Add with default params
                states.append({
                    'name': name,
                    'icon_params': {},
                    'target': {'r': r, 'g': g, 'b': b}
                })

        conn.close()
        print(f"[{fetch_timestamp}] DATABASE FETCH: Found {len(states)} Marshall states")
    except Exception as e:
        print(f"[{fetch_timestamp}] CRITICAL DATABASE ERROR: {e}")

    return states

def delete_marshall_state(name):
    """Delete a Marshall state from both database and refresh file"""
    operation_id = f"delete_{int(time.time() * 1000)}"
    success = False

    try:
        # APPROACH 1: Delete from database
        try:
            conn = sqlite3.connect('harmony_presets.db')
            cursor = conn.cursor()

            # First try the new table name
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marshall_states'")
            if cursor.fetchone():
                cursor.execute("DELETE FROM marshall_states WHERE name = ?", (name,))
            else:
                # Fall back to old table name
                cursor.execute("DELETE FROM harmony_states WHERE name = ?", (name,))

            conn.commit()
            conn.close()
            success = True
            print(f"[{operation_id}] DATABASE DELETE COMPLETED")
        except Exception as e_db:
            print(f"[{operation_id}] DATABASE DELETE FAILED: {e_db}")

        # APPROACH 2: Delete from refresh file
        try:
            refresh_timestamp = delete_saved_state(name)
            st.session_state.force_hard_refresh = refresh_timestamp
            success = True
            print(f"[{operation_id}] REFRESH FILE DELETE COMPLETED, timestamp: {refresh_timestamp}")
        except Exception as e_file:
            print(f"[{operation_id}] REFRESH FILE DELETE FAILED: {e_file}")

        if success:
            return True
        else:
            raise Exception("All delete methods failed")
    except Exception as e:
        st.error(f"Error deleting Marshall state: {e}")
        return False

def save_rendering_preset(name, params):
    """Save a rendering parameter preset to the database and refresh file"""
    operation_id = f"save_preset_{int(time.time() * 1000)}"
    success = False

    try:
        print(f"[{operation_id}] SAVING RENDERING PRESET: name={name}")

        # Convert params to JSON for database storage
        params_json = json.dumps(params)

        # APPROACH 1: Save to database
        try:
            conn = sqlite3.connect('harmony_presets.db')
            cursor = conn.cursor()

            # First ensure the table exists
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS rendering_presets (
                name TEXT PRIMARY KEY,
                params TEXT
            )
            ''')

            # Use parameterized query for safety
            cursor.execute(
                "INSERT OR REPLACE INTO rendering_presets (name, params) VALUES (?, ?)",
                (name, params_json)
            )

            # Commit and close
            conn.commit()
            conn.close()
            success = True
            print(f"[{operation_id}] DATABASE SAVE COMPLETED")
        except Exception as e_db:
            print(f"[{operation_id}] DATABASE SAVE FAILED: {e_db}")

        # APPROACH 2: ALWAYS save to refresh trigger file
        try:
            # Record in the refresh trigger file
            refresh_timestamp = record_saved_preset(name, params)

            # Set the force refresh flag in session state
            st.session_state.force_hard_refresh = refresh_timestamp

            print(f"[{operation_id}] REFRESH FILE SAVE COMPLETED, timestamp: {refresh_timestamp}")
            success = True
        except Exception as e_file:
            print(f"[{operation_id}] REFRESH FILE SAVE FAILED: {e_file}")

        # If at least one approach succeeded
        if success:
            print(f"[{operation_id}] PRESET SAVE SUCCESSFUL")
            return True
        else:
            raise Exception("All save methods failed")

    except Exception as e:
        error_msg = f"Error saving rendering preset: {e}"
        print(f"[{operation_id}] CRITICAL ERROR: {error_msg}")
        import traceback
        print(traceback.format_exc())
        st.error(error_msg)
        return False

def get_rendering_presets():
    """Get all saved rendering presets directly from database"""
    # Generate a completely unique timestamp for this fetch
    fetch_timestamp = int(time.time() * 1000000)
    print(f"[{fetch_timestamp}] FETCHING rendering presets DIRECTLY FROM DATABASE...")

    # SIMPLIFIED APPROACH: Get presets directly from the database every time
    presets = []

    try:
        # Direct database connection with fresh query
        conn = sqlite3.connect('harmony_presets.db')
        cursor = conn.cursor()

        # Query with unique fetch ID in comment to prevent caching
        cursor.execute(f"SELECT name, params FROM rendering_presets /* direct_fetch_{fetch_timestamp} */")
        rows = cursor.fetchall()

        # Process results
        for row in rows:
            name, params_json = row
            try:
                # Parse JSON for parameters
                parsed_params = json.loads(params_json) if params_json and params_json.strip() else {}

                # Add to results
                presets.append({
                    'name': name,
                    'params': parsed_params
                })
            except Exception as e:
                print(f"[{fetch_timestamp}] ERROR parsing params for {name}: {e}")
                # Add with default params
                presets.append({
                    'name': name,
                    'params': {}
                })

        conn.close()
        print(f"[{fetch_timestamp}] DATABASE FETCH: Found {len(presets)} rendering presets")
    except Exception as e:
        print(f"[{fetch_timestamp}] CRITICAL DATABASE ERROR: {e}")

    return presets

def delete_rendering_preset(name):
    """Delete a rendering preset from both database and refresh file"""
    operation_id = f"delete_preset_{int(time.time() * 1000)}"
    success = False

    try:
        # APPROACH 1: Delete from database
        try:
            conn = sqlite3.connect('harmony_presets.db')
            cursor = conn.cursor()

            cursor.execute("DELETE FROM rendering_presets WHERE name = ?", (name,))

            conn.commit()
            conn.close()
            success = True
            print(f"[{operation_id}] DATABASE DELETE COMPLETED")
        except Exception as e_db:
            print(f"[{operation_id}] DATABASE DELETE FAILED: {e_db}")

        # APPROACH 2: Delete from refresh file
        try:
            refresh_timestamp = delete_saved_preset(name)
            st.session_state.force_hard_refresh = refresh_timestamp
            success = True
            print(f"[{operation_id}] REFRESH FILE DELETE COMPLETED, timestamp: {refresh_timestamp}")
        except Exception as e_file:
            print(f"[{operation_id}] REFRESH FILE DELETE FAILED: {e_file}")

        if success:
            return True
        else:
            raise Exception("All delete methods failed")
    except Exception as e:
        st.error(f"Error deleting rendering preset: {e}")
        return False

def load_calibration():
    """Load the saved calibration from a JSON file"""
    try:
        if os.path.exists('calibration.json'):
            with open('calibration.json', 'r') as f:
                return json.load(f)
        return {'r': 1.0, 'g': 1.0, 'b': 1.0}  # Default if no calibration file
    except Exception as e:
        st.error(f"Error loading calibration: {e}")
        return {'r': 1.0, 'g': 1.0, 'b': 1.0}  # Default on error

def save_calibration(calibration_data):
    """Save calibration data to a JSON file"""
    try:
        with open('calibration.json', 'w') as f:
            json.dump(calibration_data, f)
        return True
    except Exception as e:
        st.error(f"Error saving calibration: {e}")
        return False

def get_image_base64(harmony_renderer=None, params=None, harmony_state=None, size=100):
    """Generate a base64 encoded image for display in HTML"""
    try:
        if params is None:
            params = {}

        if harmony_state is None:
            harmony_state = {'r': 1.0, 'g': 1.0, 'b': 1.0}

        # Create a small renderer with the given parameters
        small_renderer = HarmonyIndex(
            size=size,
            sigma=params.get('sigma', 0.4),
            intensity=params.get('intensity', 1.2),
            edge_blur=params.get('edge_blur', 0.5),
            edge_factor=params.get('edge_factor', 0.5)
        )

        # Set calibration if needed
        if params and 'calibrated_white_point' in params:
            small_renderer.set_calibration(params['calibrated_white_point'])

        # Render the image
        img_bytes = small_renderer.get_image_bytes(
            harmonyState=harmony_state,
            falloff_type=params.get('falloff_type', 'gaussian')
        )

        # Convert to base64
        return base64.b64encode(img_bytes).decode('utf-8')
    except Exception as e:
        st.error(f"Error generating icon: {e}")
        return None

def main():
    # Check if we have a saved layout preference
    if 'layout_preference' not in st.session_state:
        st.session_state.layout_preference = "centered"  # Default to centered layout

    # Initialize the force_hard_refresh flag if not present
    if 'force_hard_refresh' not in st.session_state:
        st.session_state.force_hard_refresh = False

    # Extreme cache-busting measure: If we're on a hard refresh cycle, add unique parameter to all query URLs
    if st.session_state.force_hard_refresh:
        timestamp = st.session_state.force_hard_refresh
        print(f"[HARD_REFRESH_{timestamp}] Applying hard refresh strategy")
        # Reset the flag immediately to prevent endless refresh loops
        last_refresh = st.session_state.force_hard_refresh
        st.session_state.force_hard_refresh = False
        # Use a special session state var to indicate post-refresh state for 5 seconds
        st.session_state.last_refresh_timestamp = last_refresh

    st.set_page_config(
        page_title="Marshall Triangle Visualization",
        page_icon="🔺",
        layout=st.session_state.layout_preference
    )

    # Apply custom CSS for colored sliders
    st.markdown(custom_slider_css(), unsafe_allow_html=True)

    # Show post-refresh indicator
    if 'last_refresh_timestamp' in st.session_state and st.session_state.last_refresh_timestamp:
        refresh_time = st.session_state.last_refresh_timestamp
        current_time = int(time.time() * 1000)
        if current_time - refresh_time < 5000:  # Show for 5 seconds
            st.success(f"⚡ Page refreshed at timestamp {refresh_time}")
        else:
            # Clear after 5 seconds
            st.session_state.last_refresh_timestamp = None

    # Create two columns for the main layout
    left_col, right_col = st.columns([0.4, 0.6], gap="medium")

    with left_col:
        st.title("The Marshall Triangle")

        # Initialize database
        init_db()

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
    if 'calibration_timestamp' not in st.session_state:
        st.session_state.calibration_timestamp = 0
    if 'show_labeled' not in st.session_state:
        st.session_state.show_labeled = False

    # Initialize session state for rendering parameters if not present
    if 'size' not in st.session_state:
        st.session_state.size = 500  # Smaller default size for side-by-side layout
    if 'falloff_type' not in st.session_state:
        st.session_state.falloff_type = 'gaussian'
    if 'sigma' not in st.session_state:
        st.session_state.sigma = 0.25
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

    # Load the saved calibration
    calibrated_white_point = load_calibration()

    # Handle preset loading and resets
    if st.session_state.reset_rendering:
        # Reset rendering parameters to default
        st.session_state.size = 1000  # Updated to 1000px per requirements
        st.session_state.falloff_type = 'gaussian'
        st.session_state.sigma = 0.25
        st.session_state.intensity = 1.0
        st.session_state.edge_blur = 0.5
        st.session_state.edge_factor = 0.5
        # Clear the flag
        st.session_state.reset_rendering = False

    if st.session_state.load_rendering_preset is not None:
        # Get the preset params
        params = st.session_state.load_rendering_preset
        # Update session state with preset values
        st.session_state.size = params.get('size', 500)
        st.session_state.falloff_type = params.get('falloff_type', 'gaussian')
        if params.get('falloff_type', 'gaussian') == 'gaussian':
            st.session_state.sigma = params.get('sigma', 0.25)
        st.session_state.intensity = params.get('intensity', 1.0)
        st.session_state.edge_blur = params.get('edge_blur', 0.5)
        st.session_state.edge_factor = params.get('edge_factor', 0.5)
        # Clear the loaded preset
        st.session_state.load_rendering_preset = None

    if st.session_state.load_state is not None:
        # Get the Marshall state
        harmony_state = st.session_state.load_state
        # Update state sliders
        st.session_state.privacy_strength = harmony_state.get('r', 1.0)
        st.session_state.performance_strength = harmony_state.get('g', 1.0)
        st.session_state.personalization_strength = harmony_state.get('b', 1.0)
        # Clear the loaded state
        st.session_state.load_state = None

    # Brief introduction
    st.markdown("""
    A novel conceptual framework for visualizing triadic balance through color harmony. The Marshall Triangle 
    represents the dynamic equilibrium between **Privacy**, **Performance**, and **Personalization**, using a
    geometric configuration with color sources at midpoints rather than vertices.
    """)

    # Initialize Marshall state from session - will be potentially updated in tabs
    marshall_state = {
        'r': st.session_state.privacy_strength,
        'g': st.session_state.performance_strength,
        'b': st.session_state.personalization_strength
    }

    # Get rendering parameters
    size = st.session_state.size
    sigma = st.session_state.sigma
    intensity = st.session_state.intensity
    edge_blur = st.session_state.edge_blur
    edge_factor = st.session_state.edge_factor
    falloff_type = st.session_state.falloff_type

    # Display calibration status if just applied
    if st.session_state.calibration_success:
        st.success("✅ Calibration applied! The visualization now treats your selected state as the balanced reference point.")
        st.session_state.calibration_success = False

    # Main visualization - always visible at the top
    harmony = HarmonyIndex(
        size=size, 
        sigma=sigma, 
        intensity=intensity,
        edge_blur=edge_blur, 
        edge_factor=edge_factor
    )

    # Apply calibration
    harmony.set_calibration(calibrated_white_point)

    # Determine whether to show labeled or unlabeled version
    show_labels = st.checkbox("Show Labels", value=st.session_state.show_labeled)
    st.session_state.show_labeled = show_labels

    # Render appropriate version of the triangle
    if show_labels:
        fig = harmony.plot_with_labels(harmonyState=marshall_state, falloff_type=falloff_type)
        st.pyplot(fig)
    else:
        img = harmony.render(harmonyState=marshall_state, falloff_type=falloff_type)
        st.image(img, caption="Marshall Triangle", use_container_width=True)

    # Simple controls below the image
    img_bytes = harmony.get_image_bytes(harmonyState=marshall_state, falloff_type=falloff_type)
    st.download_button(
        label="Download Image",
        data=img_bytes,
        file_name="marshall_triangle.png",
        mime="image/png"
    )

    # Initialize active tab tracking in session state
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0

    with right_col:
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs([
            "📐 Model Framework", 
            "⚖️ State & Calibration", 
            "🎨 Visualization Settings"
        ])

    # We'll use the session_state active_tab only for tab selection via buttons
    # but won't override it during normal rendering - this allows tab persistence

    # Tab 1: Model Framework - Theoretical explanation
    with tab1:
        # Don't change active tab on content rendering, only when tab is clicked
        st.header("Marshall Triangle: Conceptual Framework")

        st.subheader("Theoretical Foundation")
        st.markdown("""
        The Marshall Triangle represents a novel approach to visualizing dynamic triadic systems. 
        It emerged from the need to intuitively represent the balance between three conceptual poles: 
        Privacy, Performance, and Personalization.

        Unlike traditional models like Maxwell's Triangle (which places colors at vertices), 
        the Marshall Triangle positions primary colors at the midpoints of each side, 
        creating a more harmonious and balanced visual field.
        """)

        st.subheader("Structural Significance")
        st.markdown("""
        The key geometrical insights:

        - **Midpoint Sources**: Primary colors radiate inward from the midpoints of each side
        - **Emergent Secondaries**: This configuration naturally produces secondary colors (Yellow, Magenta, Cyan) at the vertices
        - **Luminous Center**: A pure white emerges at the exact geometric center when all influences are in equilibrium

        This structure serves as an intuitive model for mapping multi-polar systems where balance is the key attribute.
        """)

        st.subheader("Mathematical Model")
        st.markdown("""
        The color at any point within the triangle is determined by additive blending of contributions from each midpoint source.
        Each source's influence diminishes with distance according to selected falloff functions:

        - **Gaussian falloff**: `intensity = exp(-distance² / (2 * sigma²))`
        - **Inverse-square falloff**: `intensity = 1 / distance²`

        Colors blend additively, creating the characteristic gradient field with white at center.
        """)

        st.subheader("The White Point Concept")
        st.markdown("""
        The most significant conceptual feature is the dynamic White Point:

        - Beyond fixed reference systems, the white point in the Marshall Triangle is subjective and user-defined
        - Users can calibrate their own "optimal balance" state as the white reference point
        - The system adjusts visualization to represent this state as a balanced white
        - This creates a personalized visual feedback mechanism for maintaining preferred equilibrium
        """)

    # Tab 2: State & Calibration - Controls for adjusting and saving states
    with tab2:
        st.header("Marshall State & Calibration")

        # Marshall State Vector
        st.subheader("State Vector Controls")
        st.markdown("""
        Adjust the relative strengths of each trait. These values control the intensity
        of each color source, altering the equilibrium state of the system:
        """)

        # Privacy (Red) - with custom styling
        st.markdown("""<h5 style="color: #ff5555;">Privacy</h5>""", unsafe_allow_html=True)
        privacy_strength = st.slider(
                                   "##", 
                                   min_value=0.0, 
                                   max_value=1.0, 
                                   step=0.05,
                                   key="privacy_strength",
                                   help="Controls the intensity of the red color source (Privacy)")

        # Performance (Green) - with custom styling
        st.markdown("""<h5 style="color: #55ff55;">Performance</h5>""", unsafe_allow_html=True)
        performance_strength = st.slider(
                                      "##", 
                                      min_value=0.0, 
                                      max_value=1.0, 
                                      step=0.05,
                                      key="performance_strength",
                                      help="Controls the intensity of the green color source (Performance)")

        # Personalization (Blue) - with custom styling
        st.markdown("""<h5 style="color: #5555ff;">Personalization</h5>""", unsafe_allow_html=True)
        personalization_strength = st.slider(
                                           "##", 
                                           min_value=0.0, 
                                           max_value=1.0, 
                                           step=0.05,
                                           key="personalization_strength",
                                           help="Controls the intensity of the blue color source (Personalization)")

        # Update Marshall state
        marshall_state = {
            'r': privacy_strength,
            'g': performance_strength,
            'b': personalization_strength
        }

        # Triadic Calibration section
        st.subheader("Triadic Calibration")
        st.markdown("""
        Set your current state as your preferred "White Point of Harmony". 
        This personalizes the visualization so your chosen balance appears as white at center.
        """)

        # Display current calibration
        st.markdown(f"""
        **Current White Point Calibration:**
        - Privacy (Red): {calibrated_white_point['r']:.2f}
        - Performance (Green): {calibrated_white_point['g']:.2f}
        - Personalization (Blue): {calibrated_white_point['b']:.2f}
        """)

        # Calibration buttons
        col1, col2 = st.columns(2)

        with col1:
            calibrate_btn = st.button("Calibrate: Set Current State as White Point")

            if calibrate_btn:
                save_success = save_calibration(marshall_state)
                if save_success:
                    st.session_state.calibration_success = True
                    # Update the calibration timestamp to force reload in the main app
                    st.session_state.calibration_timestamp = time.time()
                    st.success("White Point calibrated successfully! The current state will now appear balanced (white) at the center.")
                    # Force a rerun to apply the new calibration
                    st.rerun()

        with col2:
            reset_btn = st.button("Reset Calibration")

            if reset_btn:
                default_calibration = {'r': 1.0, 'g': 1.0, 'b': 1.0}
                save_success = save_calibration(default_calibration)
                if save_success:
                    # Update the calibration timestamp to force reload
                    st.session_state.calibration_timestamp = time.time()
                    st.success("Calibration reset to default balanced state (1.0, 1.0, 1.0).")
                    # Force a rerun to apply the new calibration
                    st.rerun()

        # Save State UI
        st.subheader("Save Current Marshall State")
        state_name = st.text_input("State Name", value="", key=f"state_name_{int(time.time())}")

        # We're making the save button click a distinct state to prevent Streamlit refresh issues
        if 'save_state_clicked' not in st.session_state:
            st.session_state.save_state_clicked = False

        # Function to handle save button click
        def on_save_state_click():
            st.session_state.save_state_clicked = True
            if 'state_name' in st.session_state and st.session_state.state_name:
                name = st.session_state.state_name
                print(f"ATTEMPTING DIRECT RERUN after saving state: {name}")
                st.rerun()

        # The save button triggers a function instead of inline logic
        st.button("Save Current State", on_click=on_save_state_click, key="save_marshall_state_btn")

        # Handle the save operation in a separate code block that runs after button click
        if st.session_state.save_state_clicked and state_name:
            # Create icon parameters
            icon_params = {
                'size': 100,  # Small icon
                'sigma': sigma,
                'intensity': intensity,
                'edge_blur': edge_blur,
                'edge_factor': edge_factor,
                'falloff_type': falloff_type,
                'calibrated_white_point': calibrated_white_point
            }

            save_operation_id = f"save_{int(time.time() * 1000)}"
            print(f"[{save_operation_id}] MANUAL SAVE BUTTON CLICKED - Saving state '{state_name}'")

            # Create a message area to show the progress
            status_placeholder = st.empty()
            status_placeholder.info(f"⏳ Saving state '{state_name}'...")

            # Save state to database using our new approach
            try:
                save_success = save_marshall_state(
                    state_name, 
                    icon_params, 
                    marshall_state['r'], 
                    marshall_state['g'], 
                    marshall_state['b']
                )
            except Exception as e:
                status_placeholder.error(f"❌ Error during save operation: {e}")
                print(f"[{save_operation_id}] EXCEPTION DURING SAVE: {e}")
                import traceback
                print(traceback.format_exc())
                save_success = False

            if save_success:
                print(f"[{save_operation_id}] SAVE SUCCESS - Beginning UI refresh process")
                st.session_state.state_saved = True

                # Clear all relevant caches
                if 'marshall_states_cache' in st.session_state:
                    del st.session_state.marshall_states_cache

                # Direct verification of save (separate from the save function's own verification)
                import subprocess
                verify_cmd = f"SELECT name FROM marshall_states WHERE name = '{state_name}';"
                verify_result = subprocess.run(
                    ['sqlite3', 'harmony_presets.db', verify_cmd], 
                    capture_output=True, 
                    text=True
                )
                verification = verify_result.stdout.strip()
                print(f"[{save_operation_id}] INDEPENDENT VERIFICATION: '{verification}'")

                # Show success message with details
                st.success(f"✅ Marshall State '{state_name}' saved! Database verified: '{verification}'")
                print(f"[{save_operation_id}] FORCING PAGE RELOAD with st.rerun()")

                # Reset the button state
                st.session_state.save_state_clicked = False

                # Force a complete page reload with consistent method
                print(f"[{save_operation_id}] FORCING PAGE RELOAD with st.rerun()")
                st.rerun()
            else:
                # Show error with detailed info
                st.error(f"Failed to save state '{state_name}'. Check logs for details.")
                print(f"[{save_operation_id}] SAVE FAILED - No reload triggered")

        # Display state saved message
        if st.session_state.state_saved:
            st.success("✅ Marshall State saved successfully!")
            st.session_state.state_saved = False

        # Display preset deleted message
        if st.session_state.preset_deleted:
            st.success("✅ Preset deleted successfully!")
            st.session_state.preset_deleted = False

        # Load State UI
        st.subheader("Saved Marshall States")

        # Generate a unique key based on time to prevent caching
        fetch_timestamp = time.time()

        # Force query the database directly each time with a unique comment to avoid caching
        conn = sqlite3.connect('harmony_presets.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM marshall_states /* direct_query_{fetch_timestamp} */")
        db_states = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Display direct query results with timestamp
        with st.expander("Database Debug Info (Click to expand)"):
            st.write(f"**States in database (direct query at {fetch_timestamp}):**")
            st.code(f"{db_states}")
            st.write("If you've saved a state and it's not appearing, try refreshing your browser.")
            st.button("Sync with Database", key=f"sync_db_{int(fetch_timestamp*1000)}")

        # Get states the normal way but with a unique key and force refresh
        marshall_states = get_marshall_states()

        # Debug info
        st.write(f"Number of Marshall states found: {len(marshall_states)} (fetch timestamp: {fetch_timestamp})")

        if marshall_states:
            # Display all saved states in a grid
            num_cols = 3  # Display 3 states per row

            # Divide states into rows
            rows = [marshall_states[i:i+num_cols] for i in range(0, len(marshall_states), num_cols)]

            for row in rows:
                cols = st.columns(num_cols)

                for i, state in enumerate(row):
                    with cols[i]:
                        # Generate preview icon
                        icon_base64 = get_image_base64(
                            None,
                            state['icon_params'],
                            harmony_state={'r': state['target']['r'], 
                                          'g': state['target']['g'], 
                                          'b': state['target']['b']},
                            size=100
                        )

                        if icon_base64:
                            # Display the icon with the name as a caption
                            st.markdown(
                                f"<div style='text-align: center;'><img src='data:image/png;base64,{icon_base64}' width='100px'/><br/><b>{state['name']}</b></div>", 
                                unsafe_allow_html=True
                            )

                            # Display state values with proper abbreviations
                            st.markdown(
                                f"Pr: {state['target']['r']:.2f}, "
                                f"Pf: {state['target']['g']:.2f}, "
                                f"Ps: {state['target']['b']:.2f}"
                            )

                            # Load and Delete buttons using container
                            btn_container = st.container()
                            load_btn_key = f"load_state_{state['name']}"
                            delete_btn_key = f"delete_state_{state['name']}"

                            # Use HTML/CSS for button layout
                            btn_container.markdown(
                                f"""
                                <div style="display: flex; gap: 10px;">
                                    <div style="flex: 1;">{st.button("Load", key=load_btn_key)}</div>
                                    <div style="flex: 1;">{st.button("Delete", key=delete_btn_key)}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                            # Handle button clicks
                            if st.session_state.get(load_btn_key):
                                st.session_state.load_state = state['target']
                                st.success(f"Marshall State '{state['name']}' loaded successfully!")
                                st.rerun()

                            if st.session_state.get(delete_btn_key):
                                delete_marshall_state(state['name'])
                                st.session_state.preset_deleted = True
                                st.success(f"Marshall State '{state['name']}' deleted successfully!")
                                st.rerun()
        else:
            st.info("No Marshall states saved yet. Create one by setting your preferred state and clicking 'Save Current State'.")

    # Tab 3: Visualization Settings - Controls for adjusting the visualization and rendering presets
    with tab3:

        st.header("Visualization Settings")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Basic Parameters
            st.subheader("Basic Parameters")

            # Image size
            size = st.slider("Image Size (pixels)", 
                             min_value=500, 
                             max_value=2000, 
                             value=st.session_state.size,
                             key="size",
                             step=100)

            # Falloff function
            falloff_type = st.radio("Falloff Function", 
                                   ["gaussian", "inverse_square"],
                                   index=0 if st.session_state.falloff_type == 'gaussian' else 1,
                                   key="falloff_type")

            # Sigma (for Gaussian falloff only)
            if falloff_type == "gaussian":
                sigma = st.slider("Sigma (Gaussian falloff)", 
                                 min_value=0.05, 
                                 max_value=0.5, 
                                 value=st.session_state.sigma,
                                 key="sigma",
                                 step=0.05)
            else:
                sigma = 0.2  # Default value, not used for inverse square

            # Color intensity
            intensity = st.slider("Color Intensity", 
                                 min_value=0.1, 
                                 max_value=2.0, 
                                 value=st.session_state.intensity,
                                 key="intensity",
                                 step=0.1)

            # Advanced options
            st.subheader("Advanced Edge Smoothing")

            # Edge blur
            edge_blur = st.slider("Edge Blur Radius", 
                                min_value=0.0, 
                                max_value=2.0, 
                                value=st.session_state.edge_blur,
                                key="edge_blur",
                                step=0.1,
                                help="The radius of Gaussian blur applied to smooth edges")

            # Edge intensity factor
            edge_factor = st.slider("Edge Intensity Factor", 
                                    min_value=0.0, 
                                    max_value=1.0, 
                                    value=st.session_state.edge_factor,
                                    key="edge_factor",
                                    step=0.1,
                                    help="Intensity factor applied to edge pixels (0=transparent, 1=full opacity)")

        with col2:
            # Save Rendering Preset UI
            st.subheader("Save Rendering Presets")

            # Save preset section
            preset_name = st.text_input("Preset Name", value="", key=f"preset_name_{int(time.time())}")

            # Set up button with callback to avoid Streamlit refresh issues
            if 'save_preset_clicked' not in st.session_state:
                st.session_state.save_preset_clicked = False

            def on_save_preset_click():
                st.session_state.save_preset_clicked = True
                if 'preset_name' in st.session_state and st.session_state.preset_name:
                    name = st.session_state.preset_name
                    print(f"ATTEMPTING DIRECT RERUN after saving preset: {name}")
                    st.rerun()

            # The save button triggers a function instead of inline logic
            st.button("Save Current Settings", on_click=on_save_preset_click, key="save_rendering_preset_btn")

            # Reset Rendering Parameters button
            if st.button("Reset to Default Settings"):
                # Set the reset flag to true
                st.session_state.reset_rendering = True
                st.success("Rendering parameters reset to default values.")

            if st.session_state.save_preset_clicked and preset_name:
                # Create parameters object
                params = {
                    'size': size,
                    'falloff_type': falloff_type,
                    'sigma': sigma,
                    'intensity': intensity,
                    'edge_blur': edge_blur,
                    'edge_factor': edge_factor
                }

                # Create a message area to show the progress
                status_placeholder = st.empty()
                status_placeholder.info(f"⏳ Saving preset '{preset_name}'...")

                # Save preset to database
                try:
                    save_success = save_rendering_preset(preset_name, params)
                except Exception as e:
                    status_placeholder.error(f"❌ Error during preset save: {e}")
                    print(f"[DEBUG] EXCEPTION DURING PRESET SAVE: {e}")
                    import traceback
                    print(traceback.format_exc())
                    save_success = False

                if save_success:
                    st.session_state.rendering_preset_saved = True
                    # Get a direct count from the database to verify
                    conn = sqlite3.connect('harmony_presets.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM rendering_presets")
                    count = cursor.fetchone()[0]
                    cursor.execute("SELECT name FROM rendering_presets")
                    names = [row[0] for row in cursor.fetchall()]
                    conn.close()

                    # Reset the button click state
                    st.session_state.save_preset_clicked = False

                    # Show success message with verification info
                    st.success(f"✅ Rendering preset '{preset_name}' saved! Database verified: {count} presets")

                    # Clear session state caches that might affect refresh
                    if 'rendering_presets_cache' in st.session_state:
                        del st.session_state.rendering_presets_cache

                    print(f"[DEBUG] FORCING PAGE RELOAD with st.rerun()")
                    st.rerun()  # Use the correct modern Streamlit rerun function

            # Display preset saved message
            if st.session_state.rendering_preset_saved:
                st.success("✅ Rendering preset saved successfully!")
                st.session_state.rendering_preset_saved = False

        # Load Rendering Preset UI - full width for list of presets
        st.subheader("Saved Rendering Presets")

        # Generate a unique key based on time to prevent caching
        presets_fetch_timestamp = time.time()

        # Force query the database directly each time with a unique comment to avoid caching
        conn = sqlite3.connect('harmony_presets.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM rendering_presets /* direct_query_{presets_fetch_timestamp} */")
        db_presets = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Display direct query results with timestamp
        with st.expander("Presets Database Debug Info (Click to expand)"):
            st.write(f"**Presets in database (direct query at {presets_fetch_timestamp}):**")
            st.code(f"{db_presets}")
            st.write("If you've saved a preset and it's not appearing, try refreshing your browser.")
            st.button("Sync Presets Database", key=f"sync_presets_db_{int(presets_fetch_timestamp*1000)}")

        # Get presets the normal way but with a unique key and force refresh
        presets = get_rendering_presets()

        # Debug info
        st.write(f"Number of rendering presets found: {len(presets)} (fetch timestamp: {presets_fetch_timestamp})")

        if presets:
            # Display all presets in a grid
            num_cols = 3  # Display 3 presets per row

            # Divide presets into rows
            rows = [presets[i:i+num_cols] for i in range(0, len(presets), num_cols)]

            for row in rows:
                cols = st.columns(num_cols)

                for i, preset in enumerate(row):
                    if i < len(row):  # Make sure we don't go out of bounds
                        with cols[i]:
                            # Generate thumbnail preview
                            icon_base64 = get_image_base64(
                                None, 
                                preset['params'], 
                                marshall_state, 
                                size=100
                            )

                            if icon_base64:
                                # Display the icon with name
                                st.markdown(
                                    f"<div style='text-align: center;'><img src='data:image/png;base64,{icon_base64}' width='100px'/><br/><b>{preset['name']}</b></div>", 
                                    unsafe_allow_html=True
                                )

                                # Display all parameters
                                st.markdown(
                                    f"Size: {preset['params'].get('size', 500)}<br/>"
                                    f"Falloff: {preset['params'].get('falloff_type', 'gaussian')}<br/>"
                                    f"Intensity: {preset['params'].get('intensity', 1.0)}<br/>"
                                    f"{'Sigma: ' + str(preset['params'].get('sigma', 0.25)) if preset['params'].get('falloff_type', 'gaussian') == 'gaussian' else ''}<br/>"
                                    f"Edge Blur: {preset['params'].get('edge_blur', 0.5)}<br/>"
                                    f"Edge Factor: {preset['params'].get('edge_factor', 0.5)}"
                                    , unsafe_allow_html=True
                                )

                                # Load and Delete buttons
                                load_col, delete_col = st.columns(2)

                                with load_col:
                                    load_btn_key = f"load_preset_{preset['name']}"
                                    if st.button("Load", key=load_btn_key):
                                        st.session_state.load_rendering_preset = preset['params']
                                        st.success(f"Preset '{preset['name']}' loaded!")
                                        # Force a rerun to apply the preset
                                        st.rerun()

                                with delete_col:
                                    delete_btn_key = f"delete_preset_{preset['name']}"
                                    if st.button("Delete", key=delete_btn_key):
                                        delete_rendering_preset(preset['name'])
                                        st.session_state.preset_deleted = True
                                        st.success(f"Preset '{preset['name']}' deleted successfully!")
                                        # Force a rerun to refresh the list of presets
                                        st.rerun()
        else:
            st.info("No rendering presets saved yet. Configure your preferred visual settings and click 'Save Current Settings'.")

if __name__ == "__main__":
    main()