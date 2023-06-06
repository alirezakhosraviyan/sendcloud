
# SendCloud Assessment 

This project has been developed to assess the coding skills for Senior Software Engineer position at [sendcloud](https://www.sendcloud.nl/)



## Applications

- #### API Service :
&emsp;
The fastapi application which server couple of controllers to manage our feedly!
- #### Scheduler Service:
 &emsp; 
The background async process which is being run on a separate docker container. Because the nature of the application is async and the code is **IO-bound** then it makes more sense to use async over multithreading or multiprocessing unless parsing xml files doesn't become a problem.


## Features

- database : postgresql
- web-framework : fastapi
- poetry
- python3.11
- sqlalchemy
- asynchronous python  
- docker and docker-compose
- CI pipeline on GitHub
- more than 50 tests for services and scheduler 
## Demo

You can play around the application online or on your own machine

- cloud  -->   [http://65.21.150.157:5000](http://65.21.150.157:5000/docs)
- local machine -->  [http://0.0.0.0:5000](http://0.0.0.0:5000/docs)





## How to deploy on docker ?

- install docker and docker-compose ( ignore if you already have the docker-compose ):
```bash
   curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
````
```bash
   chmod +x /usr/local/bin/docker-compose
```

- clone the project or open up the tar file which has been sent :

```bash
  git clone https://github.com/alirezakhosraviyan/sendcloud.git
```
  or
```bash
  tar –xvzf sendcloud.tar.gz
```
`
  then 
```bash
  cd sendcloud
```

- run the application using docker-compose (recommended):

```bash
   docker-compose -f docker-compose.yaml up
```
   to clean the database in case of database mass
```bash
   docker-compose -f docker-compose.yaml down --volume
```
- open on your local machine on port **5000**

   [http://0.0.0.0:5000/docs](http://0.0.0.0:5000/docs)

## 🚀 About Me
I'm a Senior Software Engineer, you can find more about me [here](https://www.linkedin.com/in/alirezakhosravian/)

