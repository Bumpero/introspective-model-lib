import json
import yaml
from abc import ABC, abstractmethod

# Configuration Loader
class ConfigLoader:
    @staticmethod
    def load_config(file_path):
        with open(file_path, 'r') as file:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                return yaml.safe_load(file)
            elif file_path.endswith('.json'):
                return json.load(file)
            else:
                raise ValueError("Unsupported configuration file format. Use YAML or JSON.")

# Data Introspector
class DataIntrospector:
    @staticmethod
    def introspect(data):
        entities = data.get("entities", [])
        normalized_models = []

        for entity in entities:
            model = {
                "name": entity.get("name"),
                "attributes": entity.get("attributes", {}),
                "relationships": entity.get("relationships", [])
            }
            normalized_models.append(model)

        return normalized_models

# Abstract Base Class for Generators
class SchemaGenerator(ABC):
    @abstractmethod
    def generate(self, models, output_path):
        pass

# MySQL Schema Generator
class MySQLGenerator(SchemaGenerator):
    def generate(self, models, output_path):
        sql_statements = []

        for model in models:
            table_name = model['name'].lower()
            columns = [f"{name} {self._map_type(dtype)}" for name, dtype in model['attributes'].items()]
            create_table = f"CREATE TABLE {table_name} (\n    {',\n    '.join(columns)}\n);"
            sql_statements.append(create_table)

        output_file = f"{output_path}/schema.sql"
        with open(output_file, 'w') as file:
            file.write("\n\n".join(sql_statements))

    @staticmethod
    def _map_type(dtype):
        type_mapping = {
            "string": "VARCHAR(255)",
            "integer": "INT",
            "datetime": "DATETIME",
            "text": "TEXT"
        }
        return type_mapping.get(dtype, "VARCHAR(255)")

# Neo4j Schema Generator
class Neo4jGenerator(SchemaGenerator):
    def generate(self, models, output_path):
        cypher_statements = []

        for model in models:
            label = model['name']
            constraints = [f"CREATE CONSTRAINT ON (n:{label}) ASSERT n.{attr} IS UNIQUE;" for attr in model['attributes']]
            cypher_statements.extend(constraints)

        output_file = f"{output_path}/schema.cypher"
        with open(output_file, 'w') as file:
            file.write("\n\n".join(cypher_statements))

# MongoDB Schema Generator
class MongoDBGenerator(SchemaGenerator):
    def generate(self, models, output_path):
        mongo_collections = {}

        for model in models:
            collection_name = model['name'].lower()
            documents = []  # For demonstration purposes, no document generation
            mongo_collections[collection_name] = {
                "schema": model['attributes'],
                "documents": documents
            }

        output_file = f"{output_path}/schema.json"
        with open(output_file, 'w') as file:
            json.dump(mongo_collections, file, indent=4)

# Main Script
if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Generate database schemas from input data.")
    parser.add_argument("--config", required=True, help="Path to the configuration file (YAML or JSON).")
    parser.add_argument("--input", required=True, help="Path to the input data file (JSON).")
    parser.add_argument("--output", required=True, help="Path to the output directory.")
    args = parser.parse_args()

    config = ConfigLoader.load_config(args.config)
    with open(args.input, 'r') as input_file:
        input_data = json.load(input_file)

    introspector = DataIntrospector()
    models = introspector.introspect(input_data)

    os.makedirs(args.output, exist_ok=True)

    if "mysql" in config.get("databases", {}):
        mysql_generator = MySQLGenerator()
        mysql_generator.generate(models, args.output)

    if "neo4j" in config.get("databases", {}):
        neo4j_generator = Neo4jGenerator()
        neo4j_generator.generate(models, args.output)

    if "mongodb" in config.get("databases", {}):
        mongodb_generator = MongoDBGenerator()
        mongodb_generator.generate(models, args.output)

    print(f"Schemas generated successfully in {args.output}")
