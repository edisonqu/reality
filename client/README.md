## Reality Frontend Initialization

To run Reality on your local machine you need to install all the NPM dependencies using this command.

`npm install`

After the installation of the dependencies are done, we need to have a docker container setup for the local installation of the ChromaDB (local database).

If you haven't already download docker desktop here: https://www.docker.com/products/docker-desktop/

Run this command afterwards:
```
git clone git@github.com:chroma-core/chroma.git
cd chroma
docker-compose up -d --build
```

You have now installed a ChromaDB container using docker, this usually lives on the `localhost:8000` port, however you should make sure on the docker desktop application.

After this you are ready to go, initialize your client and start your electron app using the command: 

`npm start`

TODO: An update on build to run on your machine as an application. 