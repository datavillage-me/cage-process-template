# Template for a process to be deployed in the data cage

This is a sample project with a representative set of resources to deploy a data processing algorithm in a Datavillage cage.

__TL;DR__ : clone this repo and edit the `process.py` file

## Content of this repo
Apart from this file, this repo contains :

| | |
|----------|-------------|
| `requirements.txt` | the python dependencies to install, as this is a python project |
| `index.py` | the entry point executable to start the process, as declared in `datavillage.yaml`. In this example, it waits for one message on the local redis queue, processes it with `process.py`, then exits |
| `process.py` | the code that actually processes incoming events |
| `test.py` | some local tests |
| `Dockerfile` | a dockerfile to bundle the project and it's dependencies into a self contained docker image |
| `.github/workflows/release_docker_image.yaml` | sample code to build and publish the docker image via github actions |

## Deployment process
What happens when such a repo is pushed on a github repository ?

The dockerfile is being used to build a docker image that is then published on the github container registry.
You can then refer to this docker image via its registry address to make the data cage download and run it in a confidential environment

## Execution process

When starting the docker container, the following environment variables are made available :
 
| variable | description |
|----------|-------------|
| DV_TOKEN |        |
| DV_APP_ID |       |
| DV_CLIENT_ID |       |
| DV_URL |       |
| REDIS_SERVICE_HOST |       |
| REDIS_SERVICE_PORT |       |
| STOCK_XL_PATH | OPTIONAL; used in the stock quote demo.  Is the path to an xlsx file with a "symbol" column, listing the stocks that we want to get quotes for |
| FMP_API_KEY | OPTIONAL; used in the stock quote demo.  API key to financialmodelingprep.com api |

The process execution is event-driven : triggering events are sent on a local Redis queue; the executable should 
subscribe to that queue and handle events appropriately.

The events are of the form 
```
{
    userIds: <optional list of user IDs>,
    jobId: <ID of the job that this event is bound to>,
    trigger: <type of event>,
}
```


