# _**Assessment**_

## Requirements before running this application:

#### Make sure to place the AWS access and secret key in project/users/views.py file
   
## How to Run this application:

1. Create a virtual environment using the command: 
    ```virtualenv venv```
   
2. Actiavte the virtual environment using the command: 
    ```source venv/bin/activate```

3. Install all the requirements: 
    ```pip3 install -r requirements.txt```
   
4. Run the application:
    ```python3 app.py```
   
5. This also assumes you have mongo installed on your machine with the user, password and database names as admin and running on port 27017.


## How to Run this application using Docker:

If you have docker client installed on your machine, just clone this repo and type the command below:
```docker compose up -d --build```
and access the application via 
```http://localhost:5000/```
   

# Points to Consider:
1. Python3 and pip3 should be installed if you are running on your local machine without using docker
2. If running this on your local machine make sure to have the username and password of the psql as farhaan as mentioned in the project/__init__.py file and db name to be as assessment.
