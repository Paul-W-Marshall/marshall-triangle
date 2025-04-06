# Marshall Triangle API Documentation

## HarmonyIndex Class

The core component of the Marshall Triangle visualization is the HarmonyIndex class, which handles all rendering and geometric calculations.

### Basic Usage

```python
from harmony_index import HarmonyIndex

# Create a new HarmonyIndex instance
harmony = HarmonyIndex(size=500, sigma=0.4, intensity=1.2)

# Render the triangle with default parameters
image = harmony.render()

# Save the image
harmony.save_image('triangle.png')
```

### Configuration Parameters

The HarmonyIndex constructor accepts several parameters to customize the rendering:

- **size** (int): The size of the output image in pixels
- **sigma** (float): Controls the spread of the Gaussian falloff function
- **intensity** (float): Controls the brightness of the colors
- **edge_blur** (float): Amount of blur applied to the triangle edges
- **edge_factor** (float): Intensity of the edge effect

### Methods

#### set_calibration(target_white_point)
Sets the calibration target for the white point in the Marshall Triangle.

Parameters:
- **target_white_point** (dict): Dictionary with keys 'r', 'g', 'b' and values between 0.0 and 1.0

#### render(harmonyState, falloff_type)
Renders the Marshall Triangle using the specified state and falloff function.

Parameters:
- **harmonyState** (dict): Dictionary with keys 'r', 'g', 'b' and values between 0.0 and 1.0
- **falloff_type** (str): The type of falloff function to use ('gaussian' or 'inverse_square')

Returns:
- **PIL.Image.Image**: The rendered triangle image

#### save_image(filename, harmonyState, falloff_type)
Renders and saves the Marshall Triangle to a file.

Parameters:
- **filename** (str): The output filename
- **harmonyState** (dict): Dictionary with keys 'r', 'g', 'b' and values between 0.0 and 1.0
- **falloff_type** (str): The type of falloff function to use

#### plot_with_labels(harmonyState, falloff_type)
Renders the triangle with matplotlib and adds labels for the vertices and midpoints.

Parameters:
- **harmonyState** (dict): Dictionary with keys 'r', 'g', 'b' and values between 0.0 and 1.0
- **falloff_type** (str): The type of falloff function to use

Returns:
- **matplotlib.figure.Figure**: The matplotlib figure
