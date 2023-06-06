
# Sendcould Assessment 

This project has been developed to assess the coding skills for Senior Software Engineer position at [sendcloud](https://www.sendcloud.nl/)



## Applications

- #### API Service :
&emsp; &emsp; &emsp;
The fastapi application which server couple of controllers to manage our feedly!
- #### Scheduler Service:
&emsp; &emsp; &emsp; 


## Features

- database : postgresql
- web-framework : fastapi
- poetry
- python3.11
- sqlalchemy
- asynchronous python  
- docker and docker-compose
- CI pipeline on github
- more than 50 tests for services and scheduler 
## Demo

You can play around the application online or on your own machine

- cloud  -->   [http://65.21.150.157:5000](http://65.21.150.157:5000/docs)
- local machine -->  [http://0.0.0.0:5000](http://0.0.0.0:5000/docs)





## How to deploy on docker ?

- clone the project or open up the tar file which has been sent :

```bash
  git clone https://github.com/alirezakhosraviyan/sendcloud.git
  
  #or

  tar –xvzf sendcloud.tar.gz

  #then 
  
  cd sendcloud
```
- install docker and docker-compose :
```bash
   sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

   sudo chmod +x /usr/local/bin/docker-compose
 
```

- run the application using docker-compose (recommended):

```bash

   docker-compose -f docker-compose.yaml up

   # to clean the database in case of database failure
   
   docker-compose -f docker-compose.yaml down --volume

```
- to run tests: 

```bash

   docker-compose -f docker-compose-tests.yaml up

```

## Author

- [@alireza Khosravian](https://www.linkedin.com/in/alirezakhosravian/)

