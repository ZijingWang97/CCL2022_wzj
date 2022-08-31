import json


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

TYPES = ['性能故障', '部件故障']

def process(records):
    data_len = len(records)
    data_new = []
    for i in range(data_len):
        record = records[i]
        data_id = record['id']
        events = record['events']
        content = record['content']

        # label all occurrence types
        type_occur = []
        for TYPE in TYPES:
            for event in events:
                event_type = event['type']
                if event_type == TYPE:
                    type_occur.append(TYPE)
        type_occur = list(set(type_occur))

        # label triggers and arguments
        for TYPE in TYPES:
            events_typed = []
            for event in events:
                event_type = event['type']
                if event_type == TYPE:
                    events_typed.append(event)
            # label triggers
            if len(events_typed) != 0:
                triggers = []
                trigger_args = {}
                for event in events_typed:
                    trigger = event['trigger']['span']
                    if trigger not in triggers:
                        triggers.append(trigger)
                    trigger_args[str(trigger)] = trigger_args.get(str(trigger), {})
                    for arg_role in event['args']:
                        print(arg_role)
                        trigger_args[str(trigger)][arg_role] = trigger_args[str(trigger)].get(arg_role, [])
                        args_roled_spans = [item['span'] for item in event['args'][arg_role]]
                        for args_roled_span in args_roled_spans:
                            if args_roled_span not in trigger_args[str(trigger)][arg_role]:
                                trigger_args[str(trigger)][arg_role].append(args_roled_span)
                # according to trigger order, write json record
                triggers_str = [str(trigger) for trigger in triggers]  # with order
                for trigger_str in trigger_args:
                    index = triggers_str.index(trigger_str)
                    data_dict = {}
                    data_dict['id'] = data_id
                    data_dict['content'] = content
                    data_dict['occur'] = type_occur
                    data_dict['type'] = TYPE
                    data_dict['triggers'] = triggers
                    data_dict['index'] = index
                    data_dict['args'] = trigger_args[trigger_str]
                    # print(data_dict)
                    data_new.append(data_dict)
    return data_new

def main():

    dev = load_data('datasets/CCL2022/data/dev.json')
    dev = process(dev)
    write(dev, './datasets/CCL2022/cascading_sampled/dev.json')
    
    train = load_data('datasets/CCL2022/data/train.json')
    train = process(train)
    write(train, './datasets/CCL2022/cascading_sampled/train.json')
if __name__ == '__main__':
    main()
