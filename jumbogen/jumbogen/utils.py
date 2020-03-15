import pandas
import re
import json
from datetime import datetime


def generate_genus_config(config_xlsx):
    """由原始xlsx配置表生成genus.json"""
    genus_config_df = pandas.read_excel(config_xlsx, sheet_name="genus")
    # genus相关配置
    genus_config = {}
    # 时间戳
    genus_config.update({"creation_date": datetime.today().strftime('%Y-%m-%d %H:%M:%S')})
    # 按照月龄从小到大添加到config字段中
    genus_config.update({"config": []})
    # 初始化ub
    upper_boundary = 0
    for j in genus_config_df.columns[1:]:
        lower_boundary = upper_boundary
        upper_boundary = float(j)
        # 月龄上下界
        month_age = {
            "lb": lower_boundary,
            "ub": upper_boundary
        }
        # 当前月龄的记录
        current_age = {
            "month_age": month_age,
            "genus": {}
        }
        for i in genus_config_df.index:
            genus = genus_config_df.Genus[i]
            levels = re.search(r"(.*)-(.*)", genus_config_df.loc[i, j])
            # level1和level2分别是"低-中"、"中-高"的分界
            current_genus = {
                "level1": float(levels.group(1)),
                "level2": float(levels.group(2))
            }
            current_age["genus"].update({genus: current_genus})
        # 添加到genus_config中
        genus_config["config"].append(current_age)
    # 输出genus_config.json
    with open("config/genus_config.json", "w", encoding="utf-8") as genus_config_json:
        json.dump(genus_config, genus_config_json, indent=2, ensure_ascii=False)


def generate_trait_config(config_xlsx="/Users/ronnie/Documents/Andall/Codes/python/jumbogen/jumbogen/config/config.xlsx"):
    """由原始xlsx配置表生成trait.json"""
    trait_config_df = pandas.read_excel(config_xlsx, sheet_name="trait")
    # trait相关配置
    trait_config = {}
    # 时间戳
    trait_config.update({"creation_date": datetime.today().strftime('%Y-%m-%d %H:%M:%S')})
    # 以Trait_ID作为索引将内容保存到config字段中
    trait_config["config"] = {}
    for i in trait_config_df.index:
        # 检测项
        trait = trait_config_df.Trait_ID[i]
        # 菌属名
        genus = trait_config_df.Genus[i]
        # 对检测项结果的影响
        effect = trait_config_df.Effect[i]
        # 结论对应分数
        conclusion_score = {}
        # 根据列名获取结论名以及对应分数
        for score_key in trait_config_df.columns[3:]:
            conclusion_score.update({score_key: trait_config_df.loc[i, score_key]})
        # 将当前行内容添加到dict中
        current_row = {
            "effect": effect,
            "score": conclusion_score
        }
        try:
            trait_config["config"][trait].update({genus: current_row})
        except KeyError:
            trait_config["config"].update({trait:{}})
            trait_config["config"][trait].update({genus: current_row})

    # 输出trait_config.json
    out_config_path = re.sub(r"config\.xlsx", "trait_config.json", config_xlsx)
    with open(out_config_path, "w", encoding="utf-8") as trait_config_json:
        json.dump(trait_config, trait_config_json, indent=2, ensure_ascii=False, default=int)


if __name__ == "__main__":
    pass
else:
    pass
