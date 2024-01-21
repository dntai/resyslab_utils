import click, argparse, sys, os
from pprint import pformat
from collections import OrderedDict

from .parser import *

def options_common(func):
    """
    https://stackoverflow.com/questions/5409450/can-i-combine-two-decorators-into-a-single-one-in-python
    """
    options = [
        click.option("--evalf", type=str, multiple=True, default=None, show_default=True),
        click.option("--evalf-all", type=bool, default=True, show_default=True),
        click.option("--debug", type=int, default=0, show_default=True),
        click.option("--debug-info", type=bool, default=True, show_default=True),
        click.option("--verbose", type=bool, default=True, show_default=True),
    ]
    for option in options: func = option(func)
    return func
    pass # options_common

def parse_common():
    options = argparse.ArgumentParser(add_help=False)
    options.add_argument('--evalf', type=str, action="append", default=[], help = " ")
    options.add_argument('--evalf-all', type=lambda x: True if x.lower()=="true" else (False if x.lower()=="false" else None), default=True, help = " ")
    options.add_argument('--debug', type=int, default=0, help = " ")
    options.add_argument('--debug-info', type=lambda x: True if x.lower()=="true" else (False if x.lower()=="false" else None), default=True, help = " ")
    options.add_argument('--verbose', type=lambda x: True if x.lower()=="true" else (False if x.lower()=="false" else None), default=True, help = " ")
    return options
    pass # parse_common    

def process_params(ctx, params, **kwargs):
    # global scope
    global_scope = ctx.obj.get('global_scope', globals())
    
    # detect unknown_args
    unknown_args = ctx.args
    unknown_args = parse_unknown_args(unknown_args, global_scope)

    script_sdate = global_scope.get("script_sdate", "")
    method_name  = ctx.command.name

    # params
    params.update(**vars(unknown_args))
    params["method"] = method_name
    params['evalf']  = list(params.get('evalf', []))

    # eval params
    if params.get('evalf_all', True):
        parse_params(params, None, {**global_scope, **locals(), **params})
    else:        
        parse_params(params, params['evalf'], {**global_scope, **locals(), **params})

    return params # process_params

def load_app_cfg(params_cfg, global_scope = {}, reload_cfg = True, use_params_debug = False, **kwargs):
    try:
        import json5
    except ImportError as ex:
        import json as json5
    
    # load app_cfg from params_cfg["app_cfg"]
    file_cfg = {}
    if os.path.exists(params_cfg.get("app_cfg", "")) == True:
        with open(params_cfg["app_cfg"], "rt") as file:
            file_cfg = json5.load(file)
    app_cfg = file_cfg.get("app", {})
    params_cfg.update(**file_cfg.get("params", {}))
    
    # load debug params
    if use_params_debug:
        params_cfg.update(**file_cfg.get("params_debug", {}))
    
    # parse params
    params_cfg = parse_params(params_cfg, scope = {**global_scope, **app_cfg, **params_cfg})
    app_cfg = parse_params(app_cfg, scope = {**global_scope, **params_cfg, **app_cfg})
    params_cfg = parse_params(params_cfg, scope = {**global_scope, **app_cfg, **params_cfg})
    
    # reload if existings
    if reload_cfg:
        app_cfg = merge_dict(global_scope.get("app_cfg", {}), app_cfg) # reload in global_scope
        params_cfg = merge_dict(global_scope.get("params_cfg", {}), params_cfg) # reload in global_scope
    
    global_scope.update(**locals())
    return app_cfg, params_cfg
    pass # load_app_cfg

def pprint_dict(info, title = "info", keys = None, **kwargs):
    print("-"*10, title, "-" * 10)
    keys = list(info.keys()) if keys is None else keys
    for k in keys:
        if k in info:
            print(f'+ {k}: {pformat(info[k])}')
        else:
            print(k)
    print()
    pass # pprint_dict

def pprint_gdict(info, title = "info", gkeys = [], keys = None, **kwargs):
    keys = list(info.keys()) if keys is None else keys
    print(f'{"-"*10} {title} {"-"*10}')
    for k in gkeys:
        if k in info:
            if k not in [dict, OrderedDict]:
                print(f'+ {k}: {pformat(info[k])}')
            else:
                print(f'+ {k}:\n{pformat(info[k])}')
        else:
            print(k)
    print("--- Others ---")
    for k in info:
        if k not in gkeys:
            if k not in [dict, OrderedDict]:
                print(f'+ {k}: {pformat(info[k])}')
            else:
                print(f'+ {k}:\n{pformat(info[k])}')
    print()
    pass # pprint_gdict

def merge_dict(a, b):
    """
    a <- merge(a, b)
    """
    for k in b:
        if k not in a:
            a[k] = b[k]
        elif type(a[k]) in [dict, OrderedDict] and type(b[k]) in [dict, OrderedDict]:
            a[k].update(**b[k])
        else:
            a[k] = b[k]
    return a
    pass # merge_dict