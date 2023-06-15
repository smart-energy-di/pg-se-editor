Simple vue app using cytoscape.js and menu components to create a basic editor.

To build and run the containers invidually.

The cytoscape node visualiser


```
cd visualiser/

docker build -t cytoscape-vis . --network=host

docker image prune #optional - removes stage images

docker run -d --rm -p 80:80 --name cytoscape-vis cytoscape-vis
```

The basic rest app (for testing/poc)

Simple api for serving json, for testing in conjunction with the Visualiser app.

```
cd simplerest/

docker build -t simple-rest . --network=host

docker run -d --rm -p 8090:8090 -v <PATH_TO>/datafiles:/datafiles--name simple-rest simple-rest
```


To build and run with docker-compose:

Enter the correct the path for the volume in the docker-compose.yaml, then run:

```
docker-compose up -d --build 
```


Editor runs on port 80 

Api endpoint is http://localhost:8090/elements