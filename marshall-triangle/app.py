# Marshall Triangle — Interactive Application
# ===========================================
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
# ===========================================

"""
Marshall Triangle Application

Interactive visualization system for exploring triadic equilibrium
through perceptual color geometry.

Usage:
    streamlit run app.py
"""

import streamlit as st
from harmony_index import HarmonyIndex


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Marshall Triangle",
        page_icon="🔺",
        layout="wide"
    )

    st.title("Marshall Triangle")
    st.markdown("""
    **Triadic Equilibrium Visualization System**
    
    Explore balanced force relationships through perceptual color geometry.
    """)

    st.markdown("---")

    st.markdown("""
    *Copyright 2026 Fidelitas LLC — Series 1*  
    [Documentation](https://marshalltriangle.com) | 
    [Repository](https://github.com/Paul-W-Marshall/marshall-triangle) |
    Code: MIT | Figures: CC BY-NC 4.0
    """)


if __name__ == "__main__":
    main()
