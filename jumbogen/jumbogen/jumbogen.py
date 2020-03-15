import json
import pandas
import random
import sys
from datetime import datetime
from config import genus_config
from config import trait_config

version = "0.1.0"
method = "16s"
conclusion_distribution = {
    "my_distribution": 0.4,
    "population_distribution": {
        "less": 0.3,
        "equal": 0.4,
        "greater": 0.3
    }
}
class_distribution = {
    "my_distribution": 0.4,
    "population_distribution": {
        "低": 0.3,
        "中": 0.4,
        "高": 0.3
    }
}
trait_class_boundary = {
    "高": [0, 0.3],
    "中": [0.3, 0.7],
    "低": [0.7, 1.0001],
}


raw_result = pandas.read_table("tests/genus_abundance.txt")

random.seed(23)
test_month_age = {sample:random.randint(0,20) for sample in raw_result.columns[1:]}
test_gender = {sample:random.sample(["male", "female"], 1) for sample in raw_result.columns[1:]}


def parse_raw_data(raw_df=raw_result, month_age=test_month_age, gender=test_gender):
    genus_result = {}
    for sample in raw_df.columns[1:]:
        genus_result.update({sample: {
            "name": sample,
            "month_age": month_age[sample],
            "gender": gender[sample]
        }})
        for i in raw_df.index:
            genus = raw_df.loc[i, "genus"]
            cell_result = raw_df.loc[i, sample]
            genus_result[sample].update({genus:cell_result})
    return genus_result


test_results = parse_raw_data()


def parse_one_sample(sample_data):
    # 依照月龄确定使用的genus_config
    month_age = sample_data["month_age"]
    for subset in genus_config["config"]:
        if month_age < subset["month_age"]["ub"]:
            genus_config_subset = subset["genus"]
        else:
            continue
    result_json = {
        "collector_id": sample_data["name"],
        "gender": sample_data["gender"],
        "month_age": sample_data["month_age"],
        "method": method,
        "version": {
            version: str(datetime.today().isoformat(sep=' ', timespec='seconds'))
        },
        "content": {},
    }
    for trait in trait_config["config"].keys():
        trait_json = {
            "type": "quantitative",
            "algorithm": "weighted score",
        }
        trait_bacteria = {}
        for genus in trait_config["config"][trait]:
            bacteria_conclusion = {
                "value": sample_data[genus]
            }
            bacteria_conclusion.update(conclusion_distribution)
            # 确定bacteria的class结果
            if genus not in genus_config_subset.keys():
                bacteria_class_value = "未检出"
            elif sample_data[genus] == 0:
                bacteria_class_value = "未检出"
            elif sample_data[genus] < genus_config_subset[genus]["level1"]:
                bacteria_class_value = "低"
            elif sample_data[genus] <= genus_config_subset[genus]["level2"]:
                bacteria_class_value = "中"
            else:
                bacteria_class_value = "高"
            bacteria_class = {
                "value": bacteria_class_value,
                "boundary": {
                    "低": [0, genus_config_subset[genus]["level1"]],
                    "中": [genus_config_subset[genus]["level1"], genus_config_subset[genus]["level2"]],
                    "高": [genus_config_subset[genus]["level2"], 1.0001]
                }
            }
            bacteria_class.update(class_distribution)
            bacteria_score = trait_config["config"][trait][genus]["score"][bacteria_class_value]
            bacteria_effect = trait_config["config"][trait][genus]["effect"]
            trait_bacteria.update({
                genus: {
                    "type": "genus",
                    "conclusion": bacteria_conclusion,
                    "class": bacteria_class,
                    "score": bacteria_score,
                    # "effect": bacteria_effect,
                }
            })
        trait_conclusion_value = \
            sum([one_genus["score"] for _, one_genus in trait_bacteria.items()])\
            / len(trait_bacteria)
        trait_conclusion = {
            "value": trait_conclusion_value,
        }
        trait_conclusion.update(conclusion_distribution)
        if trait_conclusion_value < 0.3:
            trait_class_value = "高"
        elif trait_conclusion_value < 0.7:
            trait_class_value = "中"
        else:
            trait_class_value = "低"
        trait_class = {
            "value": trait_class_value,
        }
        trait_class.update(trait_class_boundary)
        trait_class.update(class_distribution)
        trait_json.update({
            "conclusion": trait_conclusion,
            "class": trait_class,
            "bacteria": trait_bacteria,
        })
        result_json["content"].update({
            trait: trait_json
        })
    return result_json


for sample_id, result in test_results.items():
    sample_json = parse_one_sample(result)
    with open("tests/results/" + sample_id + ".json", "w", encoding="utf-8") as out:
        json.dump(sample_json, out, indent=2, ensure_ascii=False)
