"""
Marshall Triangle Rendering Engine (HarmonyIndex)

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

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import io
from scipy import ndimage
from typing import Dict, Optional

# The HarmonyIndex class implements the Marshall Triangle visualization model
# This class renders the Marshall Triangle, a novel geometric configuration for visualizing
# triadic balance between Privacy (Red), Performance (Green), and Personalization (Blue)
#
# Canonical Parameters:
# - sigma: 0.30 (optimal Gaussian falloff for balanced color blending)
# - Valid range: 0.1-0.6 (0.30 is canonical for publication)
class HarmonyIndex:
    def __init__(self, size=500, sigma=0.30, intensity=1.2, edge_blur=0.5, edge_factor=0.5):
        self.size = size
        self.sigma = sigma
        self.intensity = intensity
        self.edge_blur = edge_blur
        self.edge_factor = edge_factor
        # Default calibration white point (balanced state)
        self.calibrated_white_point = {'r': 1.0, 'g': 1.0, 'b': 1.0}
        
    def set_calibration(self, target_white_point: Optional[Dict[str, float]] = None):
        """
        Set the calibration target for the white point in the Marshall Triangle.
        This implements the Triadic Calibration concept where any point can be defined
        as the preferred "White Point of Harmony" by the user.
        
        Parameters:
        -----------
        target_white_point : Dict[str, float], optional
            Dictionary containing normalized weights that should be rendered as white/balanced:
            {'r': float, 'g': float, 'b': float} with values between 0.0 and 1.0
            If None, uses default balanced values (1.0 for all channels)
        """
        if target_white_point is None:
            self.calibrated_white_point = {'r': 1.0, 'g': 1.0, 'b': 1.0}
            return
            
        # Ensure all values are within valid range
        self.calibrated_white_point = {}
        for key in ['r', 'g', 'b']:
            if key in target_white_point:
                self.calibrated_white_point[key] = max(0.01, min(1.0, target_white_point[key]))
            else:
                self.calibrated_white_point[key] = 1.0

    def _create_coordinate_grid(self):
        x = np.linspace(-1, 1, self.size)
        y = np.linspace(-1, 1, self.size)
        return np.meshgrid(x, y)

    def _define_triangle(self):
        height = np.sqrt(3)
        scale = 0.95  # adjust to avoid clipping at corners
        top = (0, height / 2 * scale)
        bottom_left = (-1 * scale, -height / 2 * scale)
        bottom_right = (1 * scale, -height / 2 * scale)
        return [top, bottom_left, bottom_right]

    def _calculate_midpoints(self, vertices):
        top, bottom_left, bottom_right = vertices
        return [
            ((top[0] + bottom_left[0])/2, (top[1] + bottom_left[1])/2),  # Red
            ((top[0] + bottom_right[0])/2, (top[1] + bottom_right[1])/2),  # Green
            ((bottom_left[0] + bottom_right[0])/2, (bottom_left[1] + bottom_right[1])/2)  # Blue
        ]

    def _is_inside_triangle(self, x, y, vertices):
        def sign(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

        buffer = 0.005
        v1, v2, v3 = vertices
        d1 = sign((x, y), v1, v2)
        d2 = sign((x, y), v2, v3)
        d3 = sign((x, y), v3, v1)
        return not ((d1 < -buffer or d2 < -buffer or d3 < -buffer) and
                    (d1 > buffer or d2 > buffer or d3 > buffer))

    def _gaussian_falloff(self, x, y, cx, cy):
        dist_sq = (x - cx)**2 + (y - cy)**2
        sigma = self.sigma * 1.8
        return np.exp(-dist_sq / (2 * sigma**2)) * self.intensity

    def _inverse_square_falloff(self, x, y, cx, cy):
        dist_sq = (x - cx)**2 + (y - cy)**2
        return self.intensity * 0.8 / (dist_sq + 0.05)

    def render(self, harmonyState: Optional[Dict[str, float]] = None, falloff_type='gaussian'):
        """
        Render the Marshall Triangle using a dynamic state vector to weight color intensities,
        adjusted based on the calibrated white point.
        
        Parameters:
        -----------
        harmonyState : Dict[str, float], optional
            Dictionary containing normalized weights for each color channel:
            {'r': float, 'g': float, 'b': float} with values between 0.0 and 1.0
            If None, equal weights (1.0) are used for all channels
        falloff_type : str
            The type of falloff function to use ('gaussian' or 'inverse_square')
            
        Returns:
        --------
        PIL.Image.Image
            The rendered Marshall Triangle image
        """
        # Set default harmony state if not provided
        if harmonyState is None:
            harmonyState = {'r': 1.0, 'g': 1.0, 'b': 1.0}
        
        # Ensure all values are within valid range
        for key in ['r', 'g', 'b']:
            if key not in harmonyState:
                harmonyState[key] = 1.0  # Default to 1.0 if missing
            harmonyState[key] = max(0.0, min(1.0, harmonyState[key]))  # Clamp to [0, 1]
        
        # Apply calibration by normalizing the harmonyState relative to the calibrated white point
        # This will make the calibrated white point appear balanced (white) at the center
        normalized_state = {}
        
        # Calculate the max calibration value to maintain proper scaling
        max_calibration = max(self.calibrated_white_point.values())
        
        for key in ['r', 'g', 'b']:
            # Prevent division by zero
            if self.calibrated_white_point[key] < 0.01:
                normalized_state[key] = harmonyState[key] * max_calibration
            else:
                # Scale the input state by the reciprocal of the calibrated white point
                # and multiply by the max to maintain proper brightness
                # This makes it so that when harmonyState == calibrated_white_point, the result is balanced (1.0, 1.0, 1.0)
                normalized_state[key] = harmonyState[key] * (max_calibration / self.calibrated_white_point[key])
        
        xg, yg = self._create_coordinate_grid()
        vertices = self._define_triangle()
        midpoints = self._calculate_midpoints(vertices)
        colors = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        red = np.zeros((self.size, self.size))
        green = np.zeros_like(red)
        blue = np.zeros_like(red)
        mask = np.zeros_like(red, dtype=bool)

        falloff = self._gaussian_falloff if falloff_type == 'gaussian' else self._inverse_square_falloff

        for i in range(self.size):
            for j in range(self.size):
                x, y = xg[i, j], yg[self.size - 1 - i, j]  # flip y to match image orientation
                if self._is_inside_triangle(x, y, vertices):
                    mask[i, j] = True
                    for k, (mx, my) in enumerate(midpoints):
                        val = falloff(x, y, mx, my)
                        # Apply calibrated state weighting to each color channel
                        if k == 0:  # Red (Privacy)
                            weighted_val = val * normalized_state['r']
                        elif k == 1:  # Green (Performance)
                            weighted_val = val * normalized_state['g']
                        else:  # Blue (Personalization)
                            weighted_val = val * normalized_state['b']
                        
                        red[i, j] += colors[k][0] * weighted_val
                        green[i, j] += colors[k][1] * weighted_val
                        blue[i, j] += colors[k][2] * weighted_val

        edges = ndimage.binary_dilation(mask) & ~mask
        red[edges] *= self.edge_factor
        green[edges] *= self.edge_factor
        blue[edges] *= self.edge_factor

        max_val = np.maximum.reduce([red, green, blue])
        max_val = np.maximum(max_val, 1e-10)
        norm = np.minimum(max_val, 1.0)
        mask_norm = norm > 0.1

        red[mask_norm] /= norm[mask_norm]
        green[mask_norm] /= norm[mask_norm]
        blue[mask_norm] /= norm[mask_norm]

        img_array = np.stack([np.clip(red, 0, 1),
                              np.clip(green, 0, 1),
                              np.clip(blue, 0, 1)], axis=-1)
        img_array = (img_array * 255).astype(np.uint8)
        img = Image.fromarray(img_array)

        try:
            from PIL import ImageFilter
            img = img.filter(ImageFilter.GaussianBlur(radius=self.edge_blur))
        except:
            pass

        return img
        
    def save_image(self, filename="marshall_triangle.png", harmonyState: Optional[Dict[str, float]] = None, falloff_type='gaussian'):
        """
        Render and save the Marshall Triangle image.
        
        Parameters:
        -----------
        filename : str
            The name of the output file
        harmonyState : Dict[str, float], optional
            Dictionary containing normalized weights for each color channel:
            {'r': float, 'g': float, 'b': float} with values between 0.0 and 1.0
        falloff_type : str
            The type of falloff function to use ('gaussian' or 'inverse_square')
        """
        img = self.render(harmonyState=harmonyState, falloff_type=falloff_type)
        img.save(filename)
        return img
    
    def get_image_bytes(self, harmonyState: Optional[Dict[str, float]] = None, falloff_type='gaussian', format='PNG'):
        """
        Render the Marshall Triangle and return as bytes.
        
        Parameters:
        -----------
        harmonyState : Dict[str, float], optional
            Dictionary containing normalized weights for each color channel:
            {'r': float, 'g': float, 'b': float} with values between 0.0 and 1.0
        falloff_type : str
            The type of falloff function to use ('gaussian' or 'inverse_square')
        format : str
            The image format (e.g., 'PNG', 'JPEG')
            
        Returns:
        --------
        bytes
            The image as bytes
        """
        img = self.render(harmonyState=harmonyState, falloff_type=falloff_type)
        buf = io.BytesIO()
        img.save(buf, format=format)
        return buf.getvalue()
        
    def plot_with_labels(self, harmonyState: Optional[Dict[str, float]] = None, falloff_type='gaussian'):
        """
        Plot the Marshall Triangle with labels for vertices and midpoints.
        
        Parameters:
        -----------
        harmonyState : Dict[str, float], optional
            Dictionary containing normalized weights for each color channel:
            {'r': float, 'g': float, 'b': float} with values between 0.0 and 1.0
        falloff_type : str
            The type of falloff function to use ('gaussian' or 'inverse_square')
            
        Returns:
        --------
        fig : matplotlib.figure.Figure
            The matplotlib figure
        """
        img = self.render(harmonyState=harmonyState, falloff_type=falloff_type)
        
        # Create figure with black background
        fig, ax = plt.subplots(figsize=(8, 8), facecolor='black')
        ax.set_facecolor('black')
        ax.imshow(img)
        
        # Define triangle
        vertices = self._define_triangle()
        midpoints = self._calculate_midpoints(vertices)
        
        # Scale coordinates to image space
        def scale_coord(coord):
            x, y = coord
            # Map from [-1, 1] to [0, self.size-1]
            x_scaled = int((x + 1) * (self.size - 1) / 2)
            # In image coords, y increases downward, so we invert the y coordinate
            y_scaled = int((1 - y) * (self.size - 1) / 2)
            return x_scaled, y_scaled
        
        # Get scaled coordinates
        top_vertex_scaled = scale_coord(vertices[0])
        bottom_left_scaled = scale_coord(vertices[1])
        bottom_right_scaled = scale_coord(vertices[2])
        
        red_midpoint_scaled = scale_coord(midpoints[0])   # Left side midpoint (Privacy)
        green_midpoint_scaled = scale_coord(midpoints[1])  # Right side midpoint (Performance)
        blue_midpoint_scaled = scale_coord(midpoints[2])   # Bottom side midpoint (Personalization)
        
        # Add vertex labels with adjusted positions and line breaks
        ax.annotate("Yellow\n(Privacy+Performance)", (top_vertex_scaled[0], top_vertex_scaled[1]), 
                   fontsize=10, ha='center', va='center', xytext=(0, -25), textcoords='offset points',
                   color='white', bbox=dict(boxstyle="round,pad=0.3", fc='black', alpha=0.7))
        
        ax.annotate("Magenta\n(Privacy+Personalization)", (bottom_left_scaled[0], bottom_left_scaled[1]), 
                   fontsize=10, ha='center', va='center', xytext=(-25, 20), textcoords='offset points',
                   color='white', bbox=dict(boxstyle="round,pad=0.3", fc='black', alpha=0.7))
        
        ax.annotate("Cyan\n(Performance+Personalization)", (bottom_right_scaled[0], bottom_right_scaled[1]), 
                   fontsize=10, ha='center', va='center', xytext=(25, 20), textcoords='offset points',
                   color='white', bbox=dict(boxstyle="round,pad=0.3", fc='black', alpha=0.7))
        
        # Add midpoint labels with adjusted positions
        ax.annotate("Red\n(Privacy)", (red_midpoint_scaled[0], red_midpoint_scaled[1]), 
                   fontsize=10, ha='center', va='center', xytext=(30, -5), textcoords='offset points',
                   color='white', bbox=dict(boxstyle="round,pad=0.3", fc='black', alpha=0.7))
        
        ax.annotate("Green\n(Performance)", (green_midpoint_scaled[0], green_midpoint_scaled[1]), 
                   fontsize=10, ha='center', va='center', xytext=(-30, -5), textcoords='offset points',
                   color='white', bbox=dict(boxstyle="round,pad=0.3", fc='black', alpha=0.7))
        
        ax.annotate("Blue\n(Personalization)", (blue_midpoint_scaled[0], blue_midpoint_scaled[1]), 
                   fontsize=10, ha='center', va='center', xytext=(0, 30), textcoords='offset points',
                   color='white', bbox=dict(boxstyle="round,pad=0.3", fc='black', alpha=0.7))
        
        # Add center label
        center_scaled = scale_coord((0, 0))
        ax.annotate("White\n(Balance)", (center_scaled[0], center_scaled[1]), 
                   fontsize=10, ha='center', va='center',
                   color='black', bbox=dict(boxstyle="round,pad=0.3", fc='white', alpha=0.7))
        
        ax.axis('off')
        plt.tight_layout()
        
        return fig
        
    def render_to_matplotlib(self, harmonyState: Optional[Dict[str, float]] = None, falloff_type='gaussian'):
        """
        Render the Marshall Triangle directly to a matplotlib figure without any labels.
        
        Parameters:
        -----------
        harmonyState : Dict[str, float], optional
            Dictionary containing normalized weights for each color channel:
            {'r': float, 'g': float, 'b': float} with values between 0.0 and 1.0
        falloff_type : str
            The type of falloff function to use ('gaussian' or 'inverse_square')
            
        Returns:
        --------
        fig : matplotlib.figure.Figure
            The matplotlib figure
        """
        img = self.render(harmonyState=harmonyState, falloff_type=falloff_type)
        
        # Create figure with clean margins (no padding)
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Remove axis and any padding/margins
        ax.imshow(img)
        ax.axis('off')
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0, wspace=0, hspace=0)
        
        # Remove all figure padding
        fig.patch.set_visible(False)
        
        return fig
