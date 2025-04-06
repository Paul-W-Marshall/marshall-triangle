# Marshall Triangle - Technical Documentation

## Architecture Overview

The Marshall Triangle visualization is built on a multi-layered architecture that separates the rendering logic from the user interface and state management.

### Core Components

1. **HarmonyIndex Class** (`harmony_index.py`)
   - Handles all triangle rendering and geometric calculations
   - Implements color blending algorithms and radial falloff functions
   - Provides methods for exporting to different formats (PNG, matplotlib)
   - Implements Triadic Calibration for custom white point definitions

2. **Streamlit Interface** (`app.py`)
   - Provides the user interface for interacting with the visualization
   - Manages tabs, sliders, and other UI elements
   - Handles state persistence through database and file storage

3. **Persistence Layer**
   - SQLite database for storing Marshall states and rendering presets
   - File-based refresh trigger system for state management outside of Streamlit cache
   - Calibration file for storing triadic calibration settings

## Key Concepts

### Marshall Triangle Geometry

The Marshall Triangle is an equilateral triangle where:
- The top vertex represents the Yellow secondary color (Privacy + Performance)
- The bottom-left vertex represents the Magenta secondary color (Privacy + Personalization)
- The bottom-right vertex represents the Cyan secondary color (Performance + Personalization)
- The midpoints of the triangle sides represent the primary traits:
  - Left side: Red (Privacy)
  - Right side: Green (Performance)
  - Bottom side: Blue (Personalization)
- The center represents White (balanced state of all three traits)

### Color Blending

Two methods of radial color blending are implemented:
1. **Gaussian falloff**: Smoother transitions, more gradual blending
2. **Inverse square falloff**: More defined boundaries between color regions

### Dynamic State Weighting

The visualization can be adjusted through a dynamic state vector:
```python
{
    'r': 0.8,  # Privacy strength (0.0 to 1.0)
    'g': 0.6,  # Performance strength (0.0 to 1.0) 
    'b': 0.4   # Personalization strength (0.0 to 1.0)
}
```

When a state vector is applied, it weights the color intensities of each trait, shifting the "white point" toward the dominant trait(s).

### Triadic Calibration

Triadic Calibration allows defining a custom state vector as the "balanced" state (displayed as white in the center). This enables users to set their preferred balance point, calibrating the visualization to their specific needs or preferences.

## Implementation Details

### Color Calculation

Colors are calculated per-pixel using a combination of:
1. Distance from each trait's position
2. Falloff function (Gaussian or inverse square)
3. Applied state vector weights
4. Calibration adjustments

The final color is normalized to maintain proper brightness and ensure that the calibrated state appears as white.

### State Persistence

States are persisted through both:
1. SQLite database tables (`marshall_states`, `rendering_presets`)
2. File-based refresh trigger system to overcome Streamlit caching issues

### Known Issues

- Streamlit's caching mechanism sometimes prevents UI updates when states or presets are saved
- The refresh trigger system attempts to work around this limitation by forcing re-renders
