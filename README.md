
## How to deploy on docker ?

- clone the project or open up the tar file which has been sent :

```bash
  git clone git@github.com:alirezakhosraviyan/sendcloud.git
  
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
