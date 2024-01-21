__all__ = ['parse_params', 'parse_unknown_args']

#region PARSER

def parse_params(node, 
                 keys = None, 
                 scope = {}, 
                 parent_key  = None,
                 evalf_all   = True, eval_all = False,
                 eval_action = "evalf",
                 meta_names = {
                    "evalf_all"     : "evalf_all",  # evaluating all keys in node
                    "eval_all"      : "eval_all",   # evaluating all keys in node
                    "evalf"         : "evalf",      # for evalf keys in node
                    "eval"          : "eval",       # for eval keys in node
                 }, 
                 **kwargs):
    """Parse the params in a node   
    Author: Nhu-Tai Do
    Date created : 2022/01/01
    Date modified: 2022/07/29
    
    + removing meta_names in parsing (22/07/29)
    + meta_names: mapping meta_keys in node for doing a specific task
    """
    import os, yaml
    from  collections import OrderedDict

    # make sure existing all key mapping
    meta_all_names = ["evalf_all", "eval_all", "evalf", "eval"]
    meta_names.update(**{k:k for k in meta_all_names if k not in meta_names})
    local_scope = locals()
    options = {k: local_scope[k] for k in ["parent_key", "evalf_all",  "eval_all", "eval_action", "meta_names",]}
    options.update(**kwargs)

    try:
        import json5
    except ImportError as e:
        import json as json5

    def yaml_ordered_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
        class OrderedLoader(Loader):
            pass
        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return object_pairs_hook(loader.construct_pairs(node))
        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)        

    def eval_obj(obj, scope = {}, action = "evalf"):
        try:
            if action is None or action == "evalf":
                obj = eval("f'{}'".format(obj), scope)
            elif action == "eval":
                obj = eval(obj, scope)
            else:
                pass
        except:
            pass
        return obj

    def evalf_obj(obj, scope = {}, **kwargs):
        kwargs["action"] = "evalf"
        return eval_obj(obj, scope, **kwargs)

    if type(node) in [str]:
        # inner command
        if node.startswith("eval(") and node.endswith(")"): 
            node = eval_obj(node[5:-1], scope, action = "eval")
            node = parse_params(node, scope = scope, **options)
        elif node.startswith("json(") and node.endswith(")"): 
            file_path = evalf_obj(node[5:-1], scope)
            if os.path.exists(file_path) is True:
                with open(file_path, "rt") as file: 
                    node = parse_params(json5.load(file, object_pairs_hook=OrderedDict), scope = scope, **options)
        elif node.startswith("yaml(") and node.endswith(")"): 
            file_path = evalf_obj(node[5:-1], scope)
            if os.path.exists(file_path) == True:
                with open(file_path, "rt") as file: 
                    # node = parse_params(yaml.load(file), scope = scope, **options)
                    node = parse_params(yaml_ordered_load(file), scope = scope, **options)
        else: # others
            node = eval_obj(node, scope, action = eval_action)
            if type(node) in [str] and eval_action in ["evalf"]:
                if str.isnumeric(node) or node.lower() in ['true', 'false', 'yes', 'no', 'none', 'nill']:
                    node = eval_obj(node, scope = scope, action = "eval")
                else:
                    try:
                        node = float(node)
                        node = eval_obj(node, scope = scope, action = "eval")
                    except Exception as e:
                        pass
                    pass
            pass # node (str)
    elif type(node) in [dict, OrderedDict]:
        meta_info = {
            "evalf_all"  : node.get(meta_names["evalf_all"], evalf_all),
            "eval_all"   : node.get(meta_names["eval_all"], eval_all),
            "evalf"      : node.get(meta_names["evalf"], []),
            "eval"       : node.get(meta_names["eval"], []),
        }
        for k in meta_info:
            if node.get(k):
                node.pop(k)
        
        # get keys for evaluation
        keys = keys if keys is not None else list(node.keys())
        if meta_info["evalf_all"] is True:
            meta_info['evalf'].extend([k for k in node if k not in keys])
        if meta_info["eval_all"] is True:
            meta_info['eval'].extend([k for k in node if k not in keys])         
        for v in ["eval", "evalf"]:
            keys.extend([k for k in meta_info[v] if k not in keys])
        
        # get eval_keys (key, action)
        eval_keys = []
        for key in keys: 
            find_action = [v for v in ["eval", "evalf"] if key in meta_info[v] and node.get(key) is not None] # modified (22/07/29)
            action = find_action[0] if len(find_action) > 0 else eval_action
            eval_keys.append((key, action))

        options["parent_key"] = None
        for key, action in eval_keys:
            new_scope = {**scope, **{v:node[v] for v in node if v != key}}
            options.update(parent_key = key, eval_action = action)
            node[key] = parse_params(node[key], scope = new_scope, **options)
            pass # eval_keys
        node = dict(node)
    elif type(node) in [list, tuple, set]:
        node = list(node)
        for pos, sub_node in enumerate(node):
            node[pos] = parse_params(sub_node, scope = scope, **options)

    return node
    pass # parse_params

def parse_unknown_args(unknown_args, scope = {}):
    """
    parse_unknown_args([10, 30, "--a", "10", 40, "--a", 20, "--b", "--a", "--a", 30])
    --> {'a': ['10', 20, None, 30], 'b': None}
    """
    import argparse

    unknown_params = {}
    nargs = len(unknown_args)
    for idx in range(nargs):
        item  = unknown_args[idx]
        if type(item) is str and (item.startswith("--") or item.startswith("-")):
            item = item[2:] if item.startswith("--") else item[1:]
            item = item.replace("-", "_")
            value = unknown_args[idx + 1] if idx + 1 < nargs else None
            if type(value) is str and (value.startswith("--") or value.startswith("-")): value = None
            try:
                if str.isnumeric(value): value = eval(value)
                if value.lower() in ['true', 'false', 'yes', 'no']: value = eval(value)
            except:
                pass
            if unknown_params.get(item) is None:
                unknown_params[item] = value
            elif type(unknown_params[item]) is not list:
                unknown_params[item] = [unknown_params[item], value]
            else:
                unknown_params[item].append(value)
        # if
    # for
    return argparse.Namespace(**unknown_params)
    pass # parse_unknown_args

#endregion