# Template for a process to be deployed in the data cage
## Supported build environements

tentative list :
 - npm
 - yarn
 - poetry
 - pip

## Config file

Proposal for a `datavillage.yaml` file :
```
env: npm | yarn | poetry | pip
script: build
entry: dist/index.js
```  

Should the `script` var be removed, and force the build script to a fixed name, e.g. `cage-build` ?

## Deployment process
 - install the required environment toolkit (npm, poetry, ...) 
 - run the build script in the appropriate environment

Q: add support for multiple versions of toolkits ? enforce tookits versions present in the respective descriptors (like package.json#engines) ?

## Execution process
 - run the `entry` executable that must be present as a result of the build script
