from functools import partial

from anytree import AnyNode, RenderTree
from anytree.search import findall
from anytree.exporter.jsonexporter import JsonExporter

from test_data import sample_data


def filter_func(path, the_node):
    rendered_path = "/".join([""] + [str(node.name) for node in the_node.path])
    return path == rendered_path


def path_exist(root, path):
    filter_wrapper = partial(filter_func, path)
    return findall(root, filter_=filter_wrapper)


def add_nodes(root, item, current_path):
    sub_cats = item["category"].split("/")
    # print(sub_cats)
    new_current_path = current_path
    newest_node = None
    for sub_cat in sub_cats:
        new_current_path += f"/{sub_cat}"
        exists = path_exist(root, new_current_path)
        if exists:
            exists[0].ids += [item["id"]]
            newest_node = exists[0]
        else:
            newest_node = AnyNode(
                name=sub_cat, parent=newest_node or root, ids=[item["id"]]
            )


root = AnyNode(name="stock", ids=[-1])
for item in sample_data:
    add_nodes(root, item, current_path="/stock")
# print(sample_data)

for pre, fill, node in RenderTree(root):
    print("%s%s" % (pre, node.name))

exporter = JsonExporter(indent=2, sort_keys=True)
with open("output.json", "w") as f:
    f.write(exporter.export(root))
