# SocialNet-Predict

# 数据集格式介绍
整个数据集包含三份json文件: `cosponsors.json`, `members.json`, `votes.json`, 每份文件都存入了一个list。list中的每一个元素都是一个dict。每个dict的键值对见如下举例：

### cosponsors.json 文件
包含keys:
- bill_id 提案名称
- bill_type 提案类型 
- actions_dates 提案提出时间（值为一个list，有多个时间）
- sponsor 成员id
- cosponsors 成员id （值为一个list）

- case:
{'bill_id': 'b144-104', 'bill_type': 'b', 'actions_dates': ['1996-01-03'], 'sponsor': 'O000007', 'cosponsors': []}

### members.json 文件
包含keys:
- meeting 会议第几期 （值为 102 103 ...）
- subclub 成员归属的子社团（值为0、1。 两个子社团的成员一般情况下不会发生重叠。）
- members 成员id

- case:
{'meeting': '114', 'subclub': 0, 'members': ['A000374', 'A000370', 'A000055', 'A000371', 'A000372', 'A000367', 'A000369', 'A000373', 'B001291', 'B001269', 'B001282', 'B000213', 'B001270', 'B001281', 'B000287', 'B001271', 'B001287', 'B001292', 'B001257', 'B000490', 'B001293', 'B001250', 'B001273', 'B001243', ..........]}

### votes.json 文件
包含keys:
- bill_name 提案名称
- bill_type 提案类型
- date 投票时间
- id 成员id
- group 成员组别（值为0、1）
- district， 成员所在地
- vote 投票结果。 Y/N/NV 意为 yes/no/not vote

- case:
{'bill_name': 'c5-104', 'bill_type': 'c', 'date': '1995-01-31T16:48:00-05:00', 'id': 'M000687', 'group': 1, 'district': 0, 'vote': 'NV'}


# 数据读取代码示例
```python
def cosponsors():
    with open('process_data/cosponsors.json', 'r') as f:
        data = f.read()
    parsed_data = json.loads(data)
    for item in parsed_data:
        print(item)
```

