# Overview: UI for Segment Properties in Neuroglancer
This system is designed to enable users to generate URLs that link to specific segment properties within Neuroglancer, an interactive web-based tool for visualizing 3D image data. 

The involves selecting a datastack using CAVEclient and a corresponding table from a dropdown menu, which then triggers a server-side computation to generate a URL that points directly to the configured view in Neuroglancer.

![Outline](https://github.com/aplbrain/neuroglancer-segment-properties/assets/66258538/9063501c-bb9b-433a-99c6-caf092245569)

# Setting Up
**Installation**
Upgrade pip and install required packages:
`python -m pip install --upgrade pip`
`pip install Flask caveclient pandas numpy`

**Running the Application** 
To start the server and run the application, navigate to the project directory and execute:
`python app.py`


