"""
Create a markdown code to the graph of all usecases for DPPS

You can copy paste the output in the online rendering engine: https://mermaid.live/
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
outfile = "mermaid_code.txt"

import yaml

with open(graph_file, 'r') as stream:
    try:
        graph = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

mermaid_prefix = """
flowchart LR
"""

mermaid_postfix = """
classDef todo fill:crimson,color:#fff
classDef doing fill:darkorange,color:#fff
classDef done fill:steelblue,color:#fff
classDef onhold fill:lightgrey
classDef default stroke:#333,stroke-width:4px;
"""

def _parse_graph(x, nodes={}, relations=[], parent=None, pindex=1, lvl=0):
    """
    Recursive function to parse the whole dictionnary

    :param x:
    :param nodes:
    :param relations:
    :param parent:
    :param pindex:
    :param lvl:
    :return:
    """
    i = 0
    for k, v in x.items():
        index = pindex * 10 + i

        # nodename = f"UC-DPPS-CP-{index}\\n{k}"
        nodename = f"{k}"

        # relations
        if parent is not None:
            relations.append((pindex, index))

        if isinstance(v, dict):
            tmp_nodes, tmp_relations = _parse_graph(v, parent=k, pindex=index, lvl=lvl+1)


            nodes.update(tmp_nodes)
            relations.extend(tmp_relations)
        else:
            if v is not None:
                nodename += f"\\n{v}"
        # labels
        nodes[index] = nodename
        i += 1


    return nodes, list(set(relations))  # relations  #

# keys = nodes.keys()
# level = 0
# while keys:
#
#     i = 1
#     for key in keys:
#         index = int(10**level + i)
#         # register labels
#         labels[]
#
#         # register links

nodes, relations = _parse_graph(graph)

outcode = ""
outcode += mermaid_prefix

# print labels
outcode += "\t%% List of usecases with labels\n"
for (k,v) in nodes.items():
    # outcode += "\t"
    # outcode += f"{k}({v})\n"
    outcode += f"\t{k}({v})\n"

# Print relations
outcode += "\n\n\t%% Relationships between use cases\n"
for (n1, n2) in relations:
    outcode += f"\t{n1}-->{n2}\n"

outcode += mermaid_postfix

# Write mermaid file
print(f"graph written to {outfile}")
with open(outfile, "w") as obj:
    obj.write(outcode)