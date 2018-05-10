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

    config.summary_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "summary/")
    config.checkpoint_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "checkpoint/")
    config.output_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "outputs/")
    config.output_pred_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "outputs/", "predictions")
    config.output_dif_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "outputs/", "difference")
    config.output_eval_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "outputs/", "evaluation")
    config.input_dir = os.path.join("../experiments", config.exp_name, config.sub_exp, "inputs/")

    return config