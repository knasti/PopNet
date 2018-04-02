import json
from bunch import Bunch
import os


def get_config_from_json(json_file):
    """
    Get the config from a json file
    :param json_file:
    :return: config(namespace) or config(dictionary)
    """
    # parse the configurations from the config json file provided
    with open(json_file, 'r') as config_file:
        config_dict = json.load(config_file)

    # convert the dictionary to a namespace using bunch lib
    config = Bunch(config_dict)

    return config, config_dict


def process_config(jsonfile):
    config, _ = get_config_from_json(jsonfile)

    try:
        existing_sub_exp = next(os.walk(os.path.join("../experiments", config.exp_name)))[1]
    except:
        existing_sub_exp = []

    if config.sub_exp == 'new':
        sub_exp_name = 'experiment_{}'.format(str(len(existing_sub_exp) + 1))
        config.sub_exp = sub_exp_name
        config.summary_dir = os.path.join("../experiments", config.exp_name, sub_exp_name, "summary/")
        config.checkpoint_dir = os.path.join("../experiments", config.exp_name, sub_exp_name, "checkpoint/")
        config.output_dir = os.path.join("../experiments", config.exp_name, sub_exp_name, "outputs/")
    elif config.sub_exp in existing_sub_exp:
        config.summary_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "summary/")
        config.checkpoint_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "checkpoint/")
        config.output_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "outputs/")
    else:
        print('sub experiment does not exist')
        exit()

    return config