# Marshall Triangle — Harmony Index Module
# =========================================
#
# Copyright (c) 2026 Fidelitas LLC — Series 1
# SPDX-License-Identifier: MIT
#
# This file is part of the Marshall Triangle project.
# Repository: https://github.com/Paul-W-Marshall/marshall-triangle
#
# Code License: MIT (see LICENSE-MIT)
# Figures License: CC BY-NC 4.0 (see LICENSE-CC-BY-NC-4.0)
# Conceptual Framework: All Rights Reserved (Story Protocol)
#
# Inventor: Paul Warrington Marshall
# Original Implementation: March 2025
# =========================================

"""
Harmony Index Module

Core computation module for the Marshall Triangle system.
Implements triadic equilibrium calculations and perceptual
color geometry transformations.

The HarmonyIndex class provides the mathematical foundation
for balanced force visualization using additive color theory.
"""

import numpy as np
from typing import Tuple, Optional


class HarmonyIndex:
    """
    Harmony Index computation engine for Marshall Triangle.
    
    This class implements the core algorithms for calculating
    triadic equilibrium states and rendering perceptually
    balanced color representations.
    
    Attributes:
        anchors: RGB anchor points defining the triangle vertices
        white_point: Calibrated neutral reference point
    """

    def __init__(
        self,
        anchors: Optional[Tuple[Tuple[int, int, int], ...]] = None,
        white_point: Tuple[int, int, int] = (255, 255, 255)
    ):
        """
        Initialize the HarmonyIndex engine.
        
        Args:
            anchors: Optional tuple of RGB anchor points (R, G, B vertices)
            white_point: Calibrated white point for perceptual balancing
        """
        self.anchors = anchors or (
            (255, 0, 0),    # Red vertex
            (0, 255, 0),    # Green vertex
            (0, 0, 255)     # Blue vertex
        )
        self.white_point = white_point

    def compute_barycentric(
        self,
        point: Tuple[float, float]
    ) -> Tuple[float, float, float]:
        """
        Compute barycentric coordinates for a point within the triangle.
        
        Args:
            point: (x, y) coordinates within the triangle space
            
        Returns:
            Tuple of (w1, w2, w3) barycentric weights summing to 1.0
        """
        x, y = point
        w1 = max(0.0, min(1.0, x))
        w2 = max(0.0, min(1.0, y))
        w3 = max(0.0, 1.0 - w1 - w2)
        
        total = w1 + w2 + w3
        if total > 0:
            return (w1 / total, w2 / total, w3 / total)
        return (1/3, 1/3, 1/3)

    def blend_color(
        self,
        weights: Tuple[float, float, float]
    ) -> Tuple[int, int, int]:
        """
        Blend anchor colors using barycentric weights.
        
        Args:
            weights: Barycentric weights (w1, w2, w3)
            
        Returns:
            Blended RGB color tuple
        """
        r = sum(w * a[0] for w, a in zip(weights, self.anchors))
        g = sum(w * a[1] for w, a in zip(weights, self.anchors))
        b = sum(w * a[2] for w, a in zip(weights, self.anchors))
        
        return (
            int(np.clip(r, 0, 255)),
            int(np.clip(g, 0, 255)),
            int(np.clip(b, 0, 255))
        )

    def get_equilibrium_point(self) -> Tuple[float, float, float]:
        """
        Return the equilibrium point (center of triangle).
        
        Returns:
            Barycentric coordinates of the equilibrium point
        """
        return (1/3, 1/3, 1/3)
