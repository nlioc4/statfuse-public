# StatFuse

  This project was written initially as a university programming project and morphed into various forms until the current state.
  I had a lot of fun using this project as a means to learn Python and Flask while integrating with my passion for Planetside 2 and the stats that go with it.

# Setting up a dev environment

- Download the code either by downloading a ZIP or using Git.
- Create a virtual environment in the directory using "python -m venv venv" (or python3).
- Activate the virtual environment with ".\venv\Scripts\activate" (depending on what terminal/OS is used this will be different, just look up activating a virtual environment with Python.
- Install requirements with "pip install -r .\requirements.txt".
- Use "flask run" to run the program (Changing FLASK_DEBUG in .flaskenv between 1 and 0 will toggle debug mode).



# Docker

A dockerfile and compose.yaml have been included to allow for easy deployment of the project.
