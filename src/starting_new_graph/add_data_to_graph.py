# from neo4j.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
from .config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
import json
from neo4j import GraphDatabase

def start_driver():
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    return driver


def create_node(tx, label, **kwargs):
    """ Create a node with a given label and poperties as keyword argumentes.
    Inputs:
        tx: Neo4j transaction
        label: Label for the node
        kwargs: Properties for the node
    Returns:
        The created node
    """
    # Assume 'name' is the unique property for all nodes (adjust as needed)
    unique_key = 'name'
    if unique_key not in kwargs:
        raise ValueError(f"Unique property '{unique_key}' must be provided in node properties.")
    merge_str = f'{unique_key}: ${unique_key}'
    set_str = ', '.join([f'n.{k} = ${k}' for k in kwargs if k != unique_key])
    if set_str:
        cypher = f"MERGE (n:{label} {{{merge_str}}}) SET {set_str} RETURN n"
    else:
        cypher = f"MERGE (n:{label} {{{merge_str}}}) RETURN n"
    result = tx.run(cypher, **kwargs)
    return result.single()[0]

def create_nodes(tx, label, nodes_list):
    """
    Create multiple nodes of the same label using create_node.
    
    :param tx: Neo4j transaction object
    :param label: Node label (str)
    :param nodes_list: List of dictionaries with node properties
                       Example: [{"name": "Acme Corp", "founded": 1995}, {...}]
    :return: List of created or matched nodes
    """
    created_nodes = []
    for props in nodes_list:
        node = create_node(tx, label, **props)
        created_nodes.append(node)
    return created_nodes


def create_relationship(tx, from_label, from_props, rel_type, to_label, to_props, **rel_props):
    """
    Creates a relationship between two nodes identified by their labels and properties.
    If the nodes do not exist, they will be created.
    Inputs:
        tx: Neo4j transaction
        from_label: Label of the starting node
        from_props: Properties of the starting node (dict)
        rel_type: Type of the relationship
        to_label: Label of the ending node
        to_props: Properties of the ending node (dict)
        rel_props: Properties for the relationship (keyword arguments)
    Returns:
        The created relationship"""
    from_props_str = ', '.join(f'{key}: $from_{key}' for key in from_props.keys())
    to_props_str = ', '.join(f'{key}: $to_{key}' for key in to_props.keys())
    rel_props_str = ', '.join(f'{key}: ${key}' for key in rel_props.keys())
    cypher = (
        f"MERGE (a:{from_label} {{{from_props_str}}}) "
        f"MERGE (b:{to_label} {{{to_props_str}}}) "
        f"CREATE (a)-[r:{rel_type} {{{rel_props_str}}}]->(b) "
        "RETURN r"
    )

    params = {**{f"from_{k}": v for k, v in from_props.items()}, **{f"to_{k}": v for k, v in to_props.items()}, **rel_props}
    result = tx.run(cypher, **params)
    return result.single()[0]

def create_relationships(tx, relationships_list):
    """
    Create multiple relationships using create_relationship.
    
    :param tx: Neo4j transaction object
    :param relationships_list: List of dictionaries with relationship details
           Each dictionary should have keys: from_label, from_props, rel_type, to_label, to_props, rel_props
           Example: [
               {
                   "from_label": "Company",
                   "from_props": {"name": "Acme Corp"},
                   "rel_type": "OPERATES_IN",
                   "to_label": "City",
                   "to_props": {"name": "New York"},
                   "rel_props": {"since_year": 2000}
               },
               {...}
           ]
    :return: List of created or matched relationships
    """
    created_relationships = []
    for rel in relationships_list:
        relationship = create_relationship(
            tx,
            rel["from_label"],
            rel["from_props"],
            rel["rel_type"],
            rel["to_label"],
            rel["to_props"],
            **rel.get("rel_props", {})
        )
        created_relationships.append(relationship)
    return created_relationships


def main():
    driver = start_driver()

    with open("../neo4j/schema.json") as f:
        schema = json.load(f)

    with open("../data/add_nodes_to_graph.json") as f:
        node_data = json.load(f)

    with open("../data/add_relationships_to_graph.json") as f:
        relationship_data = json.load(f)  

    with driver.session() as session:

        for node, details in schema["nodes"].items():
            for prop in details.get("unique", []):
                cypher = f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node}) REQUIRE n.{prop} IS UNIQUE"
                session.run(cypher)

        created_nodes = session.execute_write(create_nodes, "Company", node_data["Company"])
        print(f"Created {len(created_nodes)} company nodes")
        created_relationships = session.execute_write(create_relationships, relationship_data)
        print(f"Created {len(created_relationships)} relationships")

    driver.close()