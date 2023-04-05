"""For PyTorch Model ModelTree"""

import sys
import re
import traceback
import inspect
from collections import OrderedDict
from typing import List

import torch.nn as nn
from rich import print as rich_print
from rich.tree import Tree as RichTree

COLOR_NAMES = [
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "bright_black",
    "bright_red",
    "bright_green",
    "bright_yellow",
    "bright_blue",
    "bright_magenta",
    "bright_cyan",
    "bright_white",
    "grey0",
    "navy_blue",
    "dark_blue",
    "blue3",
    "blue1",
    "dark_green",
    "deep_sky_blue4",
    "dodger_blue3",
    "dodger_blue2",
    "green4",
    "spring_green4",
    "turquoise4",
    "deep_sky_blue3",
    "dodger_blue1",
    "dark_cyan",
    "light_sea_green",
    "deep_sky_blue2",
    "deep_sky_blue1",
    "green3",
    "spring_green3",
    "cyan3",
    "dark_turquoise",
    "turquoise2",
    "green1",
    "spring_green2",
    "spring_green1",
    "medium_spring_green",
    "cyan2",
    "cyan1",
    "purple4",
    "purple3",
    "blue_violet",
    "grey37",
    "medium_purple4",
    "slate_blue3",
    "royal_blue1",
    "chartreuse4",
    "pale_turquoise4",
    "steel_blue",
    "steel_blue3",
    "cornflower_blue",
    "dark_sea_green4",
    "cadet_blue",
    "sky_blue3",
    "chartreuse3",
    "sea_green3",
    "aquamarine3",
    "medium_turquoise",
    "steel_blue1",
    "sea_green2",
    "sea_green1",
    "dark_slate_gray2",
    "dark_red",
    "dark_magenta",
    "orange4",
    "light_pink4",
    "plum4",
    "medium_purple3",
    "slate_blue1",
    "wheat4",
    "grey53",
    "light_slate_grey",
    "medium_purple",
    "light_slate_blue",
    "yellow4",
    "dark_sea_green",
    "light_sky_blue3",
    "sky_blue2",
    "chartreuse2",
    "pale_green3",
    "dark_slate_gray3",
    "sky_blue1",
    "chartreuse1",
    "light_green",
    "aquamarine1",
    "dark_slate_gray1",
    "deep_pink4",
    "medium_violet_red",
    "dark_violet",
    "purple",
    "medium_orchid3",
    "medium_orchid",
    "dark_goldenrod",
    "rosy_brown",
    "grey63",
    "medium_purple2",
    "medium_purple1",
    "dark_khaki",
    "navajo_white3",
    "grey69",
    "light_steel_blue3",
    "light_steel_blue",
    "dark_olive_green3",
    "dark_sea_green3",
    "light_cyan3",
    "light_sky_blue1",
    "green_yellow",
    "dark_olive_green2",
    "pale_green1",
    "dark_sea_green2",
    "pale_turquoise1",
    "red3",
    "deep_pink3",
    "magenta3",
    "dark_orange3",
    "indian_red",
    "hot_pink3",
    "hot_pink2",
    "orchid",
    "orange3",
    "light_salmon3",
    "light_pink3",
    "pink3",
    "plum3",
    "violet",
    "gold3",
    "light_goldenrod3",
    "tan",
    "misty_rose3",
    "thistle3",
    "plum2",
    "yellow3",
    "khaki3",
    "light_yellow3",
    "grey84",
    "light_steel_blue1",
    "yellow2",
    "dark_olive_green1",
    "dark_sea_green1",
    "honeydew2",
    "light_cyan1",
    "red1",
    "deep_pink2",
    "deep_pink1",
    "magenta2",
    "magenta1",
    "orange_red1",
    "indian_red1",
    "hot_pink",
    "medium_orchid1",
    "dark_orange",
    "salmon1",
    "light_coral",
    "pale_violet_red1",
    "orchid2",
    "orchid1",
    "orange1",
    "sandy_brown",
    "light_salmon1",
    "light_pink1",
    "pink1",
    "plum1",
    "gold1",
    "light_goldenrod2",
    "navajo_white1",
    "misty_rose1",
    "thistle1",
    "yellow1",
    "light_goldenrod1",
    "khaki1",
    "wheat1",
    "cornsilk1",
    "grey100",
    "grey3",
    "grey7",
    "grey11",
    "grey15",
    "grey19",
    "grey23",
    "grey27",
    "grey30",
    "grey35",
    "grey39",
    "grey42",
    "grey46",
    "grey50",
    "grey54",
    "grey58",
    "grey62",
    "grey66",
    "grey70",
    "grey74",
    "grey78",
    "grey82",
    "grey85",
    "grey89",
    "grey93",
]


class NodeColor(object):
    color_type = "green"
    color_param = "red"
    color_main = "white"


class LayerNode(RichTree):
    def __init__(
        self,
        model_name=None,
        mclass=None,
        is_param_node=False,
        color_type=None,
        color_param=None,
        color_main=None,
        style="tree",
        guide_style="tree.line",
        expanded=True,
        highlight=False,
        add_link=False,
    ):
        self.model_name = model_name
        self.mclass = mclass
        self.is_param_node = is_param_node
        self.color_type = color_type or NodeColor.color_type
        self.color_param = color_param or NodeColor.color_param
        self.color_main = color_main or NodeColor.color_main

        label = (
            " " if self.model_name is None else f"[{self.color_main}]{self.model_name}"
        )
        if self.mclass:
            if self.is_param_node:
                label += f"[{self.color_param}]{self.mclass}"
            else:
                if add_link and self.mclass in ModelTree.N2L:
                    lk = ModelTree.N2L[self.mclass]
                    if lk and lk[0] == "/":
                        label += f"[link file://{lk}]"
                    else:
                        label += f"[link {lk}]"
                label += f"[{self.color_type}]({self.mclass})"
        self.label = label

        super().__init__(
            label,
            style=style,
            guide_style=guide_style,
            expanded=expanded,
            highlight=highlight,
        )

    def add_node(
        self,
        model_name=None,
        mclass=None,
        is_param_node=False,
        color_type=None,
        color_param=None,
        color_main=None,
        style=None,
        guide_style=None,
        expanded=True,
        highlight=False,
    ):
        node = LayerNode(
            model_name,
            mclass,
            is_param_node,
            color_type or NodeColor.color_type,
            color_param or NodeColor.color_param,
            color_main or NodeColor.color_main,
            style=self.style if style is None else style,
            guide_style=self.guide_style if guide_style is None else guide_style,
            expanded=expanded,
            highlight=self.highlight if highlight is None else highlight,
        )
        self.children.append(node)
        return node


class ModelTree(object):
    N2L = {"Conv2d": "https://pytorch.org/docs/stable/generated/torch.nn.Conv2d.html"}

    def __init__(
        self,
        model: nn.Module,
        model_name="⚫️",
        multi_layer=False,
        show_buffer=True,
        only_param=True,
        color_scheme="night",
        add_link=False,
    ):
        self.model = model
        self.model_name = model_name
        self.multi_layer = multi_layer
        self.only_param = only_param

        self.color_type = NodeColor.color_type
        self.color_main = NodeColor.color_main

        self.color_param = "bright_blue"
        self.color_fold = "yellow"
        self.color_virtual = "red"
        self.color_nongrad = "magenta"
        self.show_buffer = show_buffer

        self.root_tree = None
        self.colorify(color_scheme)
        self.create_tree(add_link)

    def colorify(self, color_scheme):
        clen = len(COLOR_NAMES)
        if color_scheme == "disable":
            for attr_name in dir(self):
                if not attr_name.startswith("__") and "color" in attr_name:
                    setattr(self, attr_name, "black")
            for attr_name in dir(NodeColor):
                if not attr_name.startswith("__") and "color" in attr_name:
                    setattr(NodeColor, attr_name, "black")
        elif color_scheme == "day":
            count = 90
            for attr_name in dir(self):
                if not attr_name.startswith("__") and "color" in attr_name:
                    setattr(self, attr_name, COLOR_NAMES[count % clen])
                    count += 5
            for attr_name in dir(NodeColor):
                if not attr_name.startswith("__") and "color" in attr_name:
                    setattr(NodeColor, attr_name, COLOR_NAMES[count % clen])
                    count += 5

    def create_tree(self, add_link):
        self.root_tree = LayerNode(self.model_name, add_link)
        self.build_tree(self.model, self.root_tree)
        self.compress(self.root_tree)
        if not self.multi_layer:
            self.fold_param_node(self.root_tree)
        return self.root_tree

    def print(self):
        rich_print(self.root_tree)

    def build_tree(self, module: nn.Module, tree: LayerNode = None):
        nm = [(n, m) for n, m in module.named_children()]
        if not nm:
            return
        else:
            for n, m in nm:
                self.fill_location(m)
                type_info = re.search(r"(?<=\').*(?=\')", str(type(m))).group()
                type_info = type_info.split(".")[-1]
                nd_ = tree.add_node(n, mclass=type_info, color_type=self.color_type)
                self.process_pnode(m, nd_)
                self.build_tree(module=m, tree=nd_)

    def fold_param_node(self, t: LayerNode, p: LayerNode = None):
        if hasattr(t, "is_param_node") and t.is_param_node:
            p.label += t.label
            return True  # indicate whether should be removed
        elif len(t.children) == 0:
            return self.only_param
        else:
            rm_idx = []
            for idx, c in enumerate(t.children):
                if self.fold_param_node(t=c, p=t):
                    rm_idx.append(idx)
            t.children = [
                t.children[i] for i in range(len(t.children)) if i not in rm_idx
            ]
            return False

    def compress(self, t: LayerNode):
        if len(t.children) == 0:
            setattr(t, "_xyz", t.label)
            return

        for _, sub_tree in enumerate(t.children):
            self.compress(sub_tree)

        t_xyz = t.label + "::" + ";".join([x._xyz for x in t.children])
        setattr(t, "_xyz", t_xyz)

        nohead_xyz_dict = OrderedDict()
        for child_id, sub_tree in enumerate(t.children):
            fname_list = sub_tree._xyz.split("::")
            if len(fname_list) == 1:
                fname = fname_list[0]
            else:
                fname = "::".join(fname_list[1:])
            if fname not in nohead_xyz_dict:
                nohead_xyz_dict[fname] = [child_id]
            else:
                nohead_xyz_dict[fname].append(child_id)

        new_childrens = []
        for groupname in nohead_xyz_dict:
            representative_id = nohead_xyz_dict[groupname][0]
            rep = t.children[representative_id]
            group_node = [t.children[idx] for idx in nohead_xyz_dict[groupname]]

            rep = self.merge_layer(group_node)
            new_childrens.append(rep)
        t.children = new_childrens

    def merge_layer(self, l: List[LayerNode]):
        def neat_expr(l: List[str]):
            def _rng(nums: List[int]):
                nums = sorted(set(nums))
                gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s + 1 < e]
                edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
                return list(zip(edges, edges))

            try:
                s = _rng([int(x.strip()) for x in l])
                s = [str(x) + "-" + str(y) for x, y in s]
                return ",".join(s)
            except Exception as e:
                return ",".join(l)

        rep = l[0]
        if len(l) == 1:
            return rep
        name_list = [x.model_name for x in l]
        info_list = [x.mclass for x in l]
        type_hint_dict = OrderedDict()
        for x, y in zip(name_list, info_list):
            if y not in type_hint_dict:
                type_hint_dict[y] = [x]
            else:
                type_hint_dict[y].append(x)

        s = ""
        names = ""
        typeinfos = ""
        for t in type_hint_dict:
            group_components = type_hint_dict[t]
            group_components = neat_expr(group_components)
            names += group_components + ","
            typeinfos += t + ","
            link_str = f"{t}" if str(t) not in ModelTree.N2L else ModelTree.N2L[str(t)]
            s += f"+[link {link_str}][bold {self.color_fold}]{group_components}[/][{self.color_type}]({t}),"
        typeinfos = typeinfos[:-1]
        rep.model_name = names[:-1]
        rep.type_info = typeinfos
        rep.label = s[:-1]
        return rep

    def get_named_params(self, m):
        res = [(n, m) for n, m in m.named_parameters()]
        if self.show_buffer:
            res += [(n, m) for n, m in m.named_buffers()]
        return res

    def fill_location(self, m):
        m_name = m._get_name()
        if m_name not in self.N2L:
            im = inspect.getmodule(type(m))
            if hasattr(im, "__file__"):
                ModelTree.N2L[m_name] = im.__file__

    def process_pnode(self, m: nn.Module, tree: LayerNode, record_grad_state=True):
        known_module = {n: c for n, c in m.named_children()}
        try:
            for n, p in self.get_named_params(m):
                if n.split(".")[0] not in known_module:
                    if len(n.split(".")) > 1:
                        raise RuntimeError(
                            f"The name field {n} should be a parameter since it doesn't appear in named_children, but it contains '.'"
                        )
                    p_shape = list(p.shape)
                    if len(p_shape) == 0:
                        continue
                    mclass = f"{n}{p_shape}"
                    if str(p.dtype) != "torch.float32":
                        mclass += "(" + str(p.dtype).split(".")[-1] + ")"
                    if str(p.device) != "cpu":
                        mclass += f"({str(p.device)})"
                    if hasattr(p, "grad") and p.grad is not None:
                            mclass += "(📈)"
                    mclass = (
                        mclass.replace(" ", "")
                        .replace("(float", "(fp")
                        .replace("(int", "(i")
                    )

                    if record_grad_state:
                        if not p.requires_grad:
                            color = self.color_nongrad
                            mclass += "❄️ "
                        else:
                            color = self.color_param
                    else:
                        color = self.color_param

                    tree.add_node(mclass=mclass, is_param_node=True, color_param=color)
        except Exception as e:
            traceback.print_exc(file=sys.stdout)


def print_model(
    model,
    model_name=None,
    only_param=True,
    multi_layer=False,
    color_scheme="night",
    add_link=False,
    show_buffer=False,
):
    v = ModelTree(
        model,
        model_name= "🌳 " + (model_name or model._get_name()),
        only_param=only_param,
        multi_layer=multi_layer,
        color_scheme=color_scheme,
        add_link=add_link,
        show_buffer=show_buffer,
    )
    v.print()

def demo():
    import torch
    from transformers import BertModel
    from hiq.vis import print_model

    model = BertModel.from_pretrained("bert-base-uncased")
    model.embeddings.word_embeddings.requires_grad = False
    model.encoder.layer[0].attention.self.query.weight.requires_grad = False
    model.encoder.layer[0].attention.output.dense.weight.requires_grad = False
    model.encoder.layer[0].attention.output.LayerNorm.weight.grad = torch.ones(768)
    model.encoder = model.encoder.cuda()
    print_model(model)

if __name__ == "__main__":
    demo()
