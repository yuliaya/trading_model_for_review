import itertools as it

def pop_element(d: dict, el):
    d1 = d.copy()
    del d1[el]
    return d1

def grid_iterator(combinations, param_names):
    for c in combinations:
        output_dict = {}
        for key, value in zip (param_names, c):
            output_dict[key] = value
        yield output_dict

def grid_search_params(*params):
    if len(params[0]) == 1 and type(list(params[0].values())[0]) == list:
        param_names = [list(d.keys())[0] for d in params]
        combinations = [p for p in it.product(*[list(dictionary.values())[0] for dictionary in params])]
        return grid_iterator(combinations, param_names)
    else:
        d = params[0]
        for param_name in d.keys():
            if type(d[param_name]) == list:
                list_of_args = [pop_element(d, param_name), {param_name: d[param_name]}]
                for arg in params[1:]:
                    list_of_args.append(arg)
                return grid_search_params(*list_of_args)
            elif type(d[param_name]) == dict:
                for param_value in d[param_name].keys():
                    list_of_args = [d[param_name][param_value], {param_name: [param_value]}]
                    for arg in params[1:]:
                        list_of_args.append(arg)
                    return grid_search_params(*list_of_args)