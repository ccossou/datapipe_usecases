"""
Create a markdown code to the graph of all usecases for DPPS

This uses PlantUML language

Create the diagram with (on linux: pip install plantuml):
plantuml plantuml.pu
"""

# dpps_groups = [""]
#
# group_usecases = {
#     "datapipe": [
#
#     ]
# }

# graph_file = "graph.yaml"
graph_file = "datapipe_graph.yaml"
outfile = "plantuml.pu"

import yaml
import sys

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


# special loader with duplicate key checking
class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = []
        has_duplicate = False
        error_message = ""
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                has_duplicate = True
                error_message += f'key="{key}" has a duplicate {key_node.start_mark}.\n'
            mapping.append(key)

        if has_duplicate:
            print("Yaml file has duplicate, quitting.")
            print(error_message)
            sys.exit()
        return super().construct_mapping(node, deep)


with open(graph_file, 'r') as stream:
    graph = yaml.load(stream, UniqueKeyLoader)
    # try:
    #     graph = yaml.load(stream, UniqueKeyLoader)
    # except yaml.YAMLError as exc:
    #     print(exc)

plantUML_prefix = """
@startuml

skinparam shadowing false

"""

plantUML_postfix = """
@enduml
"""

# label for each category
categories = {
    "generic": 99,
    "simulation": 98,
    "observation": 97,
}

def parse_yaml(d, categories):
    """

    :param d: input directory read from the yaml file
    :return:
    """



    label_str = ""
    relation_str = ""

    # label_str += f"\ttogether {{\n"
    for name, index in categories.items():
        label_str += f"\tnode {name} as {index}\n"
        # nodes[index] = name
    # label_str += f"\t}}\n"

    # sort all categories top down, expect for generic that will face them all
    first_cat = True
    for name, index in categories.items():
        if name != "generic":
            if first_cat:
                relation_str += f"\t{index}--[hidden]r-->{categories['generic']}\n"
                first_cat = False
                old_index = index
            else:
                relation_str += f"\t{old_index}-[hidden]d->{index}\n"
        # nodes[index] = name

    for usecase_id, values in d.items():
        cat = values["category"]
        name = values["title"]
        desc = values["description"]

        child = values["child"]
        if child is None:
            child = []

        if cat not in categories.keys():
            raise KeyError(f"Unknown usecase category '{cat}'. Possible values: {list(categories.keys())}")

        label_str += f'\trectangle "{name}" as {usecase_id}\n'

        if cat != "generic":
            relation_str += f"\t{categories[cat]}-r->{usecase_id}\n"
        else:
            relation_str += f"\t{usecase_id}<-l-{categories[cat]}\n"

        for ci in child:
            relation_str += f"\t{usecase_id}->{ci}\n"

    outcode = ""
    outcode += plantUML_prefix

    # print labels
    outcode += "\t' List of usecases with labels\n"
    outcode += label_str

    # Print relations
    outcode += "\n\n\t' Relationships between use cases\n"
    outcode += relation_str

    outcode += plantUML_postfix

    return outcode

outcode = parse_yaml(graph, categories)

# Write mermaid file
print(f"graph written to {outfile}")
with open(outfile, "w") as obj:
    obj.write(outcode)
