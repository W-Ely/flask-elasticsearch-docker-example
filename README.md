## Geo-Search
A GeoJSON api that searches an Area of Interest for Features from a FeatureCollection.

This api has 2 endpoints `api/v1/lines` and `api/v1/points` that take a Well-known text compliant polygon as a query string and return the lines or points intersecting accordingly.

Assumptions:
- Not providing a query string at all is invalid

Notes:
- The functional tests check that the count of the returned features is correct. It would be more concise to ensure that the objects themselves are correct. I observed this to be the case through manual testing and it would take just a bit more time to codify it.

### The service
Geo-Search is:
- powered by [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/7.4/index.html),
- served by [Gunicorn](https://docs.gunicorn.org/en/stable/),
- proxied by [Nginx](https://nginx.org/en/docs/)
- controlled by [Supervisor](http://supervisord.org/introduction.html)
- containerized by [Docker](https://docs.docker.com/engine/)
- serviced by a [Flask](https://flask.palletsprojects.com/en/1.1.x/) + [Flask-restful](https://flask-restful.readthedocs.io/en/latest/)
- documented with [Flasgger](https://github.com/flasgger/flasgger) + [Swagger](https://swagger.io/docs/)

### Dependencies
This project uses Docker, Make, and Python3

### Running
To build, start, and seed the service:
```Bash
make run
```
This starts up a flask app available on port [8080](http://localhost:8080/apidocs/).
View an interactive Swagger based portal with a couple examples for the api [here](http://localhost:8080/apidocs/).

### Development Mode
To run with hot reloading:
```Bash
make dev
```

### Testing
To run tests:
```Bash
make test
```
*These test connect to a search cluster. Sometimes `test_geometry` takes a several seconds waiting for the cluster to be ready*

### Clean Up
To remove build artifacts including images:
```Bash
make clean-all
```

### Kibana
For directly inspecting the Elasticsearch cluster:
```bash
make kibana
```
Starts a Kibana container that is accessible on port [5601](http://localhost:5601)

### Resources
- [Well-known Text](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry)
- [GeoJson Interactive Map](https://geojson.io/)
- [Elasticsearch Geo Shape](https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-shape.html) and [Geo Shape Query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-geo-shape-query.html)

### Considerations for Production
This was built quickly.  I think it has strong bones but is lacking in a few areas. Before it would be ready to go live it would at least need:
- Auth on the ES cluster: Currently all environments are setup to use a no auth Elasticsearch instance.
- Caching: While Elasticsearch is powerful, to reduce the burden of repeat queries and harden the system, a memory based cache like Redis should be considered.
- Permanent datastore:  I chose Elasticsearch for the datastore here because I've used it quite a lot for other tasks but not for something like this and thought it would be fun and effective.  That said, I don't really consider it a stable store of data.  It certainly could be given the correct failover strategy. I would lean towards having something like a Postgres database with something like PostGIS to house the data and power the search by indexing off a replica slot or some other change detection mechanism.
- Observability:  While logs can be used to some extent for monitoring, metrics and alerts based off them help instill confidence that the system is behaving as expected.
