                Hospital Information System (HIS)

Here comes Hospital Information Management System(HIMS) to make things easy and run hospital operations efficiently.

Getting Started
This can be completed by following these instructions to configure, download dependencies and compile the project.

Prerequisites
Make sure that the following are installed in your system:
    Python (Version 3.8 or later)
    pip (Python package manager)
    Virtualenv (Recommended to avoid conflicts in dependencies)
    SQLite (or any other preferred database supported by Django)
    Git (Optional, to clone the repo)

Setup Instructions

Step 1: Clone the Repository
$ git clone https://github.com/irshod/hims.git
cd hims

Step 2: Make and Activate a Virtual Environment
Create a virtual environment
python -m venv venv
Now activate the virtual environment
On Windows:
venv\Scripts\activate
On macOS/Linux:
source venv/bin/activate

Step 3: Get Required Dependencies Installed
This will install the dependencies needed, specified in the requirements. txt file.
pip install -r requirements. txt

Step 4: Set Up the Database
You will need to set up the database information in the settings. py file and find the DATABASES section.
Migrate to set up the database schema:
python manage. py makemigrations
python manage.py migrate

Step 5: Create a Superuser
Make an admin account so you can access the admin dashboard.
python manage. py createsuperuser
When prompted enter the username, email and password.

Running the Project
Start the Development Server
For server up you would use the following command:
python manage.py runserver

The app will be available at:
http://127.0.0.1:8000

Installing New Dependencies
Update the requirements if you add any new libraries or packages while developing. txt file:
pip freeze > requirements.txt

Running Tests
Run tests to make sure the system behaves as expected
python manage.py test
