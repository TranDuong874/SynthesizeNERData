import json

file_path = 'RealBusinnessCardNer.json'
output_path = 'robert_data_format.json'

with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

aggregated_data = []

for image in data:
    tokens = []
    ner_tags = []    
    for object in image['objects']:
        tokens += object['tokens']
        ner_tags += object['ner_tags']

    aggregated_data.append({
        "tokens" : tokens,
        "ner_tags" : ner_tags
    })

with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(aggregated_data, file, ensure_ascii=False, indent=4)
