"""For PyTorch Model ModelTree"""

import sys
import re
import traceback
import inspect
from collections import OrderedDict
from typing import Any, List, Optional, Union

import torch
from rich import print as rich_print
from rich.tree import Tree

import hiq.model_params
from hiq.model_params import model_parameters_stats, model_parameters_str

def is_paddle(model):
    try:
        from paddle import nn as paddle_nn
    except:
        return False
    return isinstance(model, paddle_nn.Layer)


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
    color_main = "yellow"


class LayerNode(Tree):
    def __init__(
            self,
            model_name=None,
            mclass=None,
            param_node=False,
            color_type=None,
            color_param=None,
            color_main=None,
            style="tree",
            guide_style="light_sea_green",
            expanded=True,
            highlight=False,
            add_link=False,
            ref=None,
            nid="0",
    ):
        self.model_name = model_name
        self.mclass = mclass
        self.param_node = param_node
        self.color_type = color_type or NodeColor.color_type
        self.color_param = color_param or NodeColor.color_param
        self.color_main = color_main or NodeColor.color_main
        self.ref = ref
        self.nid = nid

        label = ""
        if self.mclass:
            if self.param_node:
                label += f" |[{self.color_param}]{self.mclass}"
            else:
                if add_link and self.mclass in ModelTree.N2L:
                    lk = ModelTree.N2L[self.mclass]
                    if lk and lk[0] == "/":
                        label += f"[link file://{lk}]"
                    else:
                        label += f"[link {lk}]"
                label += f"[{self.color_type}]{self.mclass}"
        if model_name and model_name.startswith("🌳"):
            label += f"[{self.color_main}]{self.model_name}"
        else:
            label += (
                " "
                if self.model_name is None
                else f"[{self.color_main}]({self.model_name})"
            )
        label = label.strip()
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
            param_node=False,
            color_type=None,
            color_param=None,
            color_main=None,
            style=None,
            guide_style=None,
            expanded=True,
            highlight=False,
            ref=None,
            nid="0",
    ):
        node = LayerNode(
            model_name,
            mclass,
            param_node,
            color_type or NodeColor.color_type,
            color_param or NodeColor.color_param,
            color_main or NodeColor.color_main,
            style=self.style if style is None else style,
            guide_style=self.guide_style if guide_style is None else guide_style,
            expanded=expanded,
            highlight=self.highlight if highlight is None else highlight,
            ref=ref,
            nid=nid,
        )
        self.children.append(node)
        return node

    def clamp(self):
        a = LayerNode("...")
        b = LayerNode("...")
        self.children.append(b)
        self.children.insert(0, a)


class ModelTree(object):
    N2L = {"Conv2d": "https://pytorch.org/docs/stable/generated/torch.nn.Conv2d.html"}

    def __init__(
            self,
            model: torch.nn.Module,
            model_name="⚫️",
            multi_layer=False,
            show_buffer=True,
            only_param=True,
            color_scheme="night",
            add_link=False,
            max_depth=1000,
            only_names=None,
            only_types=None,
            show_nid=False,
            only_nid=None,
    ):
        self.model = model
        self.model_name = model_name
        self.multi_layer = multi_layer
        self.only_param = only_param

        self.color_type = NodeColor.color_type
        self.color_main = NodeColor.color_main

        self.color_param = "bright_blue"
        self.color_fold = "magenta1"
        self.color_nongrad = "purple"
        self.show_buffer = show_buffer
        self.show_nid = show_nid
        self.only_nid = only_nid

        self.max_depth = max_depth
        self.only_names = only_names
        self.only_types = only_types
        self.root_tree = None
        self.tid = "."
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
        self.build_tree(self.model, self.root_tree, nid="0")
        self.compress(self.root_tree)
        if not self.multi_layer:
            self.fold_param_node(self.root_tree)
        if self.only_nid and self.only_nid != "0":
            self.root_tree.clamp()
        return self.root_tree

    def print(self):
        rich_print(self.root_tree)

    def build_tree(
            self, module: torch.nn.Module, tree: LayerNode = None, lid=0, nid=""
    ):
        nm = [(n, m) for n, m in module.named_children()]
        lid = lid + 1
        if not nm or lid > self.max_depth:
            return
        else:
            count = 0
            for n, m in nm:
                count += 1
                if self.only_names is not None:
                    if n not in self.only_names:
                        continue
                self.fill_location(m)
                type_info = re.search(r"(?<=\').*(?=\')", str(type(m))).group()
                type_info = type_info.rsplit(".", maxsplit=1)[-1]
                if self.only_types is not None:
                    if type_info not in self.only_types:
                        continue
                if hasattr(m, "bits"):
                    type_info += f'-{m.bits}b'
                nid_ = nid + f".{count}"
                nd_ = tree.add_node(
                    n,
                    mclass=type_info,
                    color_type=self.color_type,
                    expanded=True,
                    ref=m,
                    nid=nid_,
                )
                self.process_pnode(m, nd_, lid=lid, nid=nid_)
                self.build_tree(module=m, tree=nd_, lid=lid, nid=nid_)

    def fold_param_node(self, t: LayerNode, p: LayerNode = None):
        if hasattr(t, "param_node") and t.param_node:
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

    def compress(self, t: LayerNode, dep=0):
        # if dep==0 and self.only_nid and self.only_nid!='0' and self.only_nid!='0.1':
        #    t.add_node('***')
        if len(t.children) == 0:
            setattr(t, "_xyz", t.label)
            return

        for _, sub_tree in enumerate(t.children):
            self.compress(sub_tree, dep=dep + 1)

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
        for gn in nohead_xyz_dict:
            representative_id = nohead_xyz_dict[gn][0]
            node_ = t.children[representative_id]
            group_node = [t.children[idx] for idx in nohead_xyz_dict[gn]]
            node_ = self.merge_layer(group_node)
            if self.only_nid is not None:
                if not node_.nid.startswith(self.only_nid):
                    continue
            new_childrens.append(node_)
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

        node_ = l[0]
        if len(l) == 1:
            if not node_.param_node and self.show_nid:
                node_.label = node_.nid + "-" + node_.label
            return node_
        name_list = [x.model_name for x in l]
        info_list = [x.mclass for x in l]
        h_ = OrderedDict()
        for x, y in zip(name_list, info_list):
            if y not in h_:
                h_[y] = [x]
            else:
                h_[y].append(x)

        s, names, tinfo_ = "", "", ""
        for t in h_:
            g_ = neat_expr(h_[t])
            names += g_ + ","
            tinfo_ += t + ","
            link_str = f"{t}" if str(t) not in ModelTree.N2L else ModelTree.N2L[str(t)]
            s += f"💠 [link {link_str}][bold {self.color_fold}]{t}[/][{self.color_type}]({g_}),"
        tinfo_ = tinfo_[:-1]
        node_.model_name = names[:-1]
        node_.type_info = tinfo_
        if s[0] == "💠":
            node_.guide_style = f"bold {self.color_fold}"
            node_.highlight = True
            s = s[:-1] + f"<🦜:{model_parameters_str(node_.ref)}x{len(l)}>"
        else:
            s = s[:-1]
        if self.show_nid:
            node_.label = node_.nid + "-" + s
        else:
            node_.label = s
        return node_

    def get_named_params(self, m):
        res = [(n, m) for n, m in m.named_parameters()]
        if self.show_buffer:
            res += [(n, m) for n, m in m.named_buffers()]
        return res

    def fill_location(self, m):
        m_name = get_model_name(m)
        if m_name not in self.N2L:
            im = inspect.getmodule(type(m))
            if hasattr(im, "__file__"):
                ModelTree.N2L[m_name] = im.__file__

    def process_pnode(
            self, m: torch.nn.Module, tree: LayerNode, record_grad_state=True, lid=0, nid=""
    ):
        import os
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
                    if not str(p.dtype).endswith("float32"):
                        mclass += "<" + str(p.dtype).rsplit(".", maxsplit=1)[-1] + ">"
                    if 'HIQ_VIS_GPU' in os.environ and str(os.environ['HIQ_VIS_GPU']) == '1':
                        if hasattr(p, "device"):
                            if str(p.device) != "cpu":
                                mclass += f"<{str(p.device)}>"
                        elif hasattr(p, "place") and p.place.is_gpu_place():
                            mclass += f'<{str(p.place).replace("Place(", "").replace(")", "")}>'
                    if hasattr(p, "grad") and p.grad is not None:
                        mclass += "<📈>"
                    mclass = (
                        mclass.replace(" ", "")
                        .replace("<float", "<f")
                        .replace("<int", "<i")
                    )
                    if str(m).startswith('Conv2d'):
                        if m.groups > 1:
                            mclass += f'🇬 -{m.groups}'
                        if str(m.stride) != '(1, 1)':
                            mclass += f"🇸 -{m.stride}"
                        if str(m.dilation) != '(1, 1)':
                            mclass += f"🇩 -{m.dilation}"
                    if record_grad_state:
                        if hasattr(p, "requires_grad") and not p.requires_grad:
                            color = self.color_nongrad
                            mclass += "❄️ "
                        else:
                            color = self.color_param
                    else:
                        color = self.color_param
                    tree.add_node(
                        mclass=mclass, param_node=True, color_param=color, nid=nid
                    )
        except Exception as e:
            traceback.print_exc(file=sys.stdout)


def get_model_name(m):
    if hasattr(m, "_get_name"):
        return m._get_name()
    if hasattr(m, "_full_name"):  # paddle
        return m._full_name
    return str(type(m))


def print_model(
        model: Any,
        model_name: Optional[str] = None,
        only_param: bool = True,
        multi_layer: bool = False,
        color_scheme: str = "night",
        add_link: bool = False,
        show_buffer: bool = False,
        max_depth: int = 1000,
        only_names: Optional[List[str]] = None,
        only_types: Optional[List[str]] = None,
        show_nid: bool = False,
        only_nid: Optional[Union[str, int]] = None,
        legend: bool = False
) -> None:
    try:
        if is_paddle(model):
            global model_parameters_stats, model_parameters_str
            model_parameters_stats = hiq.model_params.model_parameters_stats_paddle
            model_parameters_str = hiq.model_params.model_parameters_str_paddle
        trainable_params, all_params, pct = model_parameters_stats(model)
        if trainable_params == all_params:
            tree_info = (
                f"<all params:{trainable_params}>" if trainable_params is not None else ""
            )
        else:
            tree_info = (
                f"<trainable_params:{trainable_params},all_params:{all_params},percentage:{pct:.5f}%>"
                if trainable_params is not None
                else ""
            )
        v = ModelTree(
            model,
            model_name="🌳 " + (model_name or get_model_name(model)) + tree_info,
            only_param=only_param,
            multi_layer=multi_layer,
            color_scheme=color_scheme,
            add_link=add_link,
            show_buffer=show_buffer,
            max_depth=max_depth,
            only_names=only_names,
            only_types=only_types,
            show_nid=show_nid,
            only_nid=only_nid,
        )
        v.print()
        if legend:
            vis_help()
    except AttributeError as e:
        print(f"WARNING: {str(e)}")


def vis_help():
    print("(🌳 : Model root, "
          "💠 : Folded layers, "
          "📈 : With gradient, "
          "❄️ : Frozen Layer, "
          "🦜 : Parameter info as `<trainable,all params x layner_number>`)")
    print("For more details, please visit: https://github.com/oracle/hiq")


def demo():
    import torch
    from transformers import BertModel

    model = BertModel.from_pretrained("bert-base-uncased")
    model.embeddings.word_embeddings.requires_grad = False
    model.encoder.layer[0].attention.self.query.weight.requires_grad = False
    model.encoder.layer[0].attention.output.dense.weight.requires_grad = False
    model.encoder.layer[0].attention.output.LayerNorm.weight.grad = torch.ones(768)
    model.encoder = model.encoder.cuda()
    print_model(model)


if __name__ == "__main__":
    vis_help()
    demo()
