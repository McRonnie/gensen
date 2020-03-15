import json
import pandas

#example_jumbo_path = "/Users/ronnie/Documents/Andall/RaD/Prod/Jumbo_Prod_v0.1.5_20200114-json-200211/50K_S1.json"
example_jumbo_path = "/Users/ronnie/Documents/Andall/RaD/Prod/Jumbo_Prod_v0.1.6_20200212_dev_with_json/50K_S1.json"
with open(example_jumbo_path) as i:
    example_jumbo = json.load(i)

def check_cs(input_doc, jumbo=example_jumbo):
    """检查concluson_source是否与jumbo一致"""
    trait_info = pandas.read_excel(input_doc, sheet_name="trait_info")
    for i in trait_info.index:
        cs = trait_info.Conclusion_Source[i]
        cs1 = cs.split(".")[0]
        trait = trait_info.Trait_ID[i]
        if cs1 not in jumbo["content"][trait[:13]].keys():
            raise ValueError(f"{trait}检测项Conslusion_Source有误")
        else:
            pass
    print("conclusion_source无误")

def check_df(input_doc):
    """检查trait_info和conclusion_info的Trait_ID一致性"""
    doc = pandas.read_excel(input_doc, sheet_name=None)
    if set(doc["trait_info"].Trait_ID) != set(doc["conclusion_info"].Trait_ID):
        raise ValueError("trait_info与conclusion_info的Trait_ID不一致")
    else:
        print("trait_info与conclusion_info的Trait_ID一致")

def check_conclusion(input_doc, jumbo=example_jumbo):
    """检查conclusion_info中的conclusion是否与jumbo中一致"""
    doc = pandas.read_excel(input_doc, sheet_name=None)
    trait_cs = {
        doc["trait_info"].Trait_ID[i]:
        doc["trait_info"].Conclusion_Source[i].split(".")[0]
        for i in doc["trait_info"].index
        }
    conclusion_codes = {x:[] for x in doc["conclusion_info"].Trait_ID}
    for i in doc["conclusion_info"].index:
        trait = doc["conclusion_info"].Trait_ID[i]
        conclusion_code = doc["conclusion_info"].Conclusion_Code[i]
        conclusion_codes[trait] = conclusion_codes[trait] + [conclusion_code]
    for trait_full, cc in conclusion_codes.items():
        trait = trait_full[:13]
        cc_in_jumbo = jumbo["content"][trait][trait_cs[trait_full]]["population_distribution"].keys()
        if set(cc_in_jumbo) != set(cc):
            raise ValueError(f"{trait_full}的conclusion_code与jumbo中不一致")
    print("conclusion_code无误")

def check_all(input_doc, jumbo=example_jumbo):
    check_cs(input_doc, jumbo=example_jumbo)
    check_df(input_doc)
    check_conclusion(input_doc, jumbo=example_jumbo)
