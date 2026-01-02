# Neo4j POC

This repository is designed to show an example of how to ingest and produce a large Neo4j graph.

## Requirements

This project currently runs locally on macOS using the following commands:

- `brew install neo4j`
- `brew services start neo4j`
- `brew services list` *(to check that the Neo4j service is running)*

If you encounter any issues, you can restart the service with:

- `brew services stop neo4j`
- `brew services start neo4j`

Once the service is running, open your browser of choice and navigate to:

`http://localhost:7474/browser/`

You can connect via authentication. By default, both the username and password are `neo4j`. You will be prompted to change this password after logging in.

You should now be connected to the local Neo4j service. You can use the `Cypher` query language directly in the prompt window in the browser to experiment and view the resulting graph.

## Helpful commands

Some helpful commands to create basic nodes and relationships are:

- `MERGE (p:Person {name: "Tom Hanks"})`  
Creates a `Person` node with the property `name = "Tom Hanks"`.

- `MERGE (m:Movie {title: "Apollo 13"})`  
Creates a `Movie` node with the property `title = "Apollo 13"`.

- 
```cypher
MATCH (p:Person {name: "Tom Hanks"})
MATCH (m:Movie {title: "Apollo 13"})
MERGE (p)-[r:ACTED_IN {role: "Jim Lovell"}]->(m)
```

## Running the Python Script

The script includes a schema that represents which nodes and relationships are available and which properties they are allowed to have. Before running the script, ensure the graph is clean by running:

`MATCH (n) DETACH DELETE n`

This query finds all nodes, removes all relationships, and then deletes the nodes.

**NOTE:** To delete a node, all relationships must be removed first. The `DETACH DELETE` command above is the quickest way to do this, but be careful—you should always know what data you are deleting.

Once the repository is cloned, you can run the script with:

`python main.py`

This constructs the nodes and relationships defined in the JSON files under the `data` directory. To view the entire graph you have just constructed, run:

`MATCH (n) RETURN n`
