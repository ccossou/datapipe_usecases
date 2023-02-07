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

plantUML_prefix = """
@startuml

skinparam shadowing false
skinparam linetype ortho
left to right direction
skinparam  rectangle {
    BackgroundColor<<generic>> #cccccc
    BackgroundColor<<simulation>> APPLICATION
    BackgroundColor<<observation>> DarkCyan
    BorderColor black
}
skinparam  usecase {
    RoundCorner 2
    BackgroundColor white
    BorderColor black
}
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

    sorted_cases = {}
    for k, v in d.items():
        cat = v["category"]
        if cat not in sorted_cases.keys():
            sorted_cases[cat] = {}

        sorted_cases[cat][k] = v

    label_str = ""
    relation_str = ""

    # we want to process the generic category at the end
    cat_list = list(categories.keys())
    cat_list.remove("generic")
    cat_list.append("generic")


    gen_index = categories["generic"]

    for category in cat_list:
        try:
            cat_index = categories[category]
        except KeyError:
            raise KeyError(f"Unknown usecase category '{category}'. Possible values: {list(categories.keys())}")

        label_str += f'\trectangle " " <<{category}>> as {cat_index} {{\n'

        if category != "generic":
            relation_str += f"\t{cat_index}--[hidden]-->{gen_index}\n"

        for usecase_id, values in sorted_cases[category].items():
            name = values["title"]
            desc = values["description"]

            child = values["child"]
            if child is None:
                child = []

            label_str += f'\tusecase "{name}" as {usecase_id}\n'

            for ci in child:
                relation_str += f"\t{usecase_id}<--{ci}\n"

        label_str += f'\t}}\n'

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
