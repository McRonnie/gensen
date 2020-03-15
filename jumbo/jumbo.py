import json
import pandas

example_jumbo_path = "/Users/ronnie/Documents/Andall/RaD/Prod/Jumbo_Prod_v0.1.5_20200114-json-200211/50K_S1.json"
with open(example_jumbo_path) as i:
    example_jumbo = json.load(i)

def check_cs(input_doc, jumbo=example_jumbo):
    trait_info = pandas.read_excel(input_doc, sheet_name="trait_info")
    for i in trait_info.index:
        cs = trait_info.Conclusion_Source[i]
        cs1 = cs.split(".")[0]
        trait = trait_info.Trait_ID[i]
        if not cs1 in jumbo["content"][trait[:13]].keys():
            raise ValueError(f"{trait}检测项Conslusion_Source有误")
        else:
            pass
    print("conclusion_source无误")