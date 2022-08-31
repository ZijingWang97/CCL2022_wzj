import hashlib
from html import entities
import json
import re


def load_data_without_label(file):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    records = []
    for line in lines:
        print(line)
        record = line
        records.append(record) 
    return records

def load_data(file):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    records = []
    
    for line in lines:
        # print(line)
        record = json.loads(line)
        records.append(record)
    return records

def write(data, fn):
    with open(fn, 'w', encoding='utf-8') as f:
        for line in data:
            line = json.dumps(line, ensure_ascii=False)
            f.write(line + '\n')



def process(records):
    data_len = len(records)
    data_new = []
    
    m=hashlib.md5()
      
    for i in range(data_len):
        record = records[i]
        m.update(str(i).encode("utf-8"))
        data_id = m.hexdigest()   
        content = record['text']
        
        # print(content)
        
        dict_event={}
        dict_list={}
        dict_event['type']=record['relation']
        dict_event['trigger']={}
        dict_event['trigger']["span"]=record['t']['pos']
        dict_event['trigger']["word"]=record['t']['name']
        dict_event['args']={}
        dict_event['args']['unit']=[{'span':record['h']['pos'],'word':record['h']['name']}]
        events = [dict_event]
        
        dict_list['id']=data_id
        dict_list['content']=content
        dict_list['events']=events
        print(dict_list)
        # label all occurrence types
        data_new.append(dict_list)

               
                    
    return data_new

def process_without_label(records):
    data_len = len(records)
    data_new = []
    
    m=hashlib.md5()
    # print(type(record['id'].encode("utf-8")))
    
    
    for i in range(data_len):
        record = records[i]
        print(record)
        m.update(str(i).encode("utf-8"))
        data_id = m.hexdigest()   

        dict_list={}
        
        dict_list['id']=data_id
        dict_list['content']=record
        print(dict_list)
        data_new.append(dict_list)

               
                    
    return data_new



def main():
    train = load_data('datasets/CCL2022/data_original/train.json')
    train = process(train)
    write(train, 'datasets/CCL2022/data/train.json')
    test=load_data_without_label('datasets/CCL2022/data_original/test_txt.json')
    test= process_without_label(test)
    write(test, 'datasets/CCL2022/data/test.json')   



if __name__ == '__main__':
    main()
