import hashlib
from html import entities
import json
import re
import copy

# {"text": "直流母线电压异常现象：运行人员工作站发出直流母线电压异常等告警信号。直流母线电压过高或者过低。", "spo_list": [{"h": {"name": "直流母线电压", "pos": [34, 40]}, "t": {"name": "过高", "pos": [40, 42]}, "relation": "性能故障"}, {"h": {"name": "直流母线", "pos": [0, 4]}, "t": {"name": "电压异常", "pos": [4, 8]}, "relation": "部件故障"}, {"h": {"name": "直流母线", "pos": [20, 24]}, "t": {"name": "电压异常", "pos": [24, 28]}, "relation": "部件故障"}, {"h": {"name": "直流母线电压", "pos": [34, 40]}, "t": {"name": "过低", "pos": [44, 46]}, "relation": "性能故障"}]}

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
    
      
    for i in range(data_len):
        record = records[i]
        text = record['content']

        dict_spolist=[]
        dict_list={}
        dict_spolist_one={}
        dict_spolist_h={}
        dict_spolist_t={}
        events = record['events']
        # print(events)
        for event in events:
            # print(event["args"]["unit"])
            if event["args"]["unit"]!=[]:
                for h in event["args"]["unit"]:
                    # print (h)
                    dict_spolist_h["name"]=h["word"]
                    dict_spolist_h["pos"]=h["span"]
                    dict_spolist_t["name"]=event["trigger"]["word"]
                    dict_spolist_t["pos"]=event["trigger"]["span"]  
                    dict_spolist_one["h"]=dict_spolist_h
                    dict_spolist_one["t"]=dict_spolist_t
                    dict_spolist_one["relation"]=event["type"]
                    # print(dict_spolist_one)
                    dict_spolist.append(copy.deepcopy(dict_spolist_one))
                    # print(dict_spolist)
            else:
                dict_spolist_t["name"]=event["trigger"]["word"]
                dict_spolist_t["pos"]=event["trigger"]["span"]  
                dict_spolist_one["h"]=dict_spolist_h
                dict_spolist_one["t"]=dict_spolist_t
                dict_spolist_one["relation"]=event["type"]
                dict_spolist.append(copy.deepcopy(dict_spolist_one))
                       
        dict_list["text"]=text
        dict_list["spo_list"]=dict_spolist  
        # dict_event['type']=record['relation']
        # dict_event['trigger']={}
        # dict_event['trigger']["span"]=record['t']['pos']
        # dict_event['trigger']["word"]=record['t']['name']
        # dict_event['args']={}
        # dict_event['args']['unit']=[{'span':record['h']['pos'],'word':record['h']['name']}]
        
        
        # dict_list['id']=data_id
        # dict_list['content']=content
        # dict_list['events']=events
        # print(dict_list)
        # # label all occurrence types
        data_new.append(copy.deepcopy(dict_list))

               
                    
    return data_new

def main():
    train = load_data('models_save/results_conf.json')
    train = process(train)
    write(train, 'results.json')

if __name__ == '__main__':
    main()
