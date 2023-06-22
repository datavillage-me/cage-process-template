# Template for a process to be deployed in the data cage

This is a sample project with a representative set of resources to deploy a data processing algorithm in a Datavillage cage.

__TL;DR__ : clone this repo and edit the `process.py` file


## Template Use case

To make this template closer to a real use case,
it implements a very simple use case of an algorithm that is waiting for an event of type 'QUOTE' and when received does the following:
 1. push an audit log (long duration logs) via the "audit_log" function to preserve that this event occured for a long period
 2. read an excel file that was uploaded in the collaboration space at path 'STOCK_XL_PATH' and containing a list of stock market shares.
 3. reach an external financial API using 'FMP_API_KEY' authentication key to get the latest quotes for the previously listed stock market shares.
 4. build a new excel file containing the quotes associated to each symbol and store it '/resources/outputs/stocks.xlsx' for possible retrieval through the collaboration space output API.
 5. store the quotes in an RDF format and push it to the SOLID pod of all end users connected to the collaboration space (if any).

All these steps are defined in the "update_quote_event_processor" function of the process.py file.
Simply adapt this function when addressing your own use case


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

The main python files index.py and process.py are pretty small thanks to the dv-utils sdk library that is simplifying a lot the code logic.
This library take care of interacting with the Datavillage middleware, the REDIS event queue and the LOKI log server.  
The default event listener defined in dv-utils is responsible for fetching and dispatching events as well as handling error during the event processing and reporting the event processing time through loki logs. 

## Deployment process
What happens when such a repo is pushed on a github repository ?

The dockerfile is being used to build a docker image that is then published on the github container registry.
You can then refer to this docker image via its registry address to make the data cage download and run it in a confidential environment

## Execution process

When running the docker container in a datavillage collaboration space, the following environment variables are made available :
 
| variable | description |
|----------|-------------|
| DV_TOKEN |  Private token used to authenticate and interact with the datavillage middleware API      |
| DV_APP_ID | The id of the collaboration space, used to authenticate with the datavillage middleware API       |
| DV_URL | The URL hosting the datavillage middleware API      |
| REDIS_SERVICE_HOST |  The IP address on which the REDIS server (and its event queue) is hosted     |
| REDIS_SERVICE_PORT |  The PORT used by the REDIS server    |

In addition, all environment variables that you define in the collaboration space are also available.
For instance the two following variables are provided and used for the stock quote demo.
| variable | description |
|----------|-------------|
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


