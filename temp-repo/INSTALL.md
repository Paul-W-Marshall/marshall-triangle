# Installation Guide

## Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

## Step 1: Clone the Repository
Clone the repository from GitHub:

    git clone https://github.com/Fidelitas-llc/marshall-triangle-visualization.git
    cd marshall-triangle-visualization

## Step 2: Install Dependencies
Install required Python packages:

    pip install -r requirements.txt

## Step 3: Run the Application
Start the Streamlit application:

    streamlit run app.py

The application will open in your default web browser at http://localhost:5000.

## Configuration

### Streamlit Configuration
The application is configured to run in headless mode on port 5000 by default. To change this, modify the .streamlit/config.toml file.

### Database
The application uses SQLite for persistence. The database file harmony_presets.db will be created automatically when you first run the application.

## Troubleshooting

### Database Issues
If you encounter database issues, you can try running the migration script:

    python migrate_db.py

This will migrate any legacy data to the new schema.

### Display Problems
If the triangle display does not render correctly, try adjusting the rendering parameters in the UI under the "Rendering" tab.