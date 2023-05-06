import json
import matplotlib.pyplot as plt

import memberNet

# 文件路径
path = './process_data/'


def read_data():
    with open(path + 'cosponsors.json', 'r') as fp:
        cosponsors_data = json.load(fp)
    with open(path + 'members.json', 'r') as fp:
        members_data = json.load(fp)
    with open(path + 'votes.json', 'r') as fp:
        votes_data = json.load(fp)

    # 删除时间为空的cosponsors数据
    for x in cosponsors_data:
        if len(x['actions_dates']) == 0:
            cosponsors_data.remove(x)
    # 删除没有被投票表决的cosponsors数据
    # print(len(cosponsors_data))
    bill_names = set(d['bill_name'] for d in votes_data)
    left = 0
    for x in cosponsors_data:
        if x['bill_id'] in bill_names:
            cosponsors_data[left] = x
            left += 1
    del cosponsors_data[left:]
    # print(len(cosponsors_data))
    # 按时间排序cosponsors_data
    cosponsors_data = sorted(cosponsors_data, key=lambda x: x['actions_dates'])
    # 字典存bill_id在cosponsors_data中的位置 (cosponsors_data中的bill_id是不重复的)
    bill_id_dict = {}
    for i in range(len(cosponsors_data)):
        x = cosponsors_data[i]
        bill_id_dict[x['bill_id']] = i
    # 删除不在cosponsors_data中的vote数据
    # print(len(votes_data))
    left = 0
    for x in votes_data:
        if bill_id_dict.get(x['bill_name']) is not None:
            votes_data[left] = x
            left += 1
    del votes_data[left:]
    # print(len(votes_data))
    # 按投票对应提案的时间先后排序votes_data
    votes_data = sorted(votes_data, key=lambda x: bill_id_dict[x['bill_name']])

    return cosponsors_data, members_data, votes_data


def main():
    cosponsors_data, members_data, votes_data = read_data()
    # print(len(set(d['id'] for d in votes_data)))

    # 记录成员在每个会议中属于哪个子社团
    subclub_dict = {}
    for x in members_data:
        meeting = x['meeting']
        subclub = x['subclub']
        for member in x['members']:
            if member not in subclub_dict:
                subclub_dict[member] = {}
                subclub_dict[member][meeting] = subclub

    net1 = memberNet.MemberNet()

    # 以提案来划分训练集和测试集
    n = len(cosponsors_data)
    n1 = int(0.8 * n)
    # 在训练集范围中更新网络
    j = 0
    for i in range(n1):
        print(i)
        cosponsor = cosponsors_data[i]
        meeting = cosponsor['bill_id'].split('-')[-1]
        # 该提案的所有投票 votes_data[j0]--votes_data[j]
        j0 = j
        while j < len(votes_data) and votes_data[j]['bill_name'] == cosponsor['bill_id']:
            if not net1.has_node(votes_data[j]['id']):
                member_subclub = None
                if votes_data[j]['id'] in subclub_dict:
                    member_subclub = subclub_dict[votes_data[j]['id']]
                net1.add_node(votes_data[j]['id'], votes_data[j]['group'], votes_data[j]['district'], member_subclub=member_subclub)
            j += 1
        print(str(j0) + '-' + str(j))
        # print(len(set(votes_data[t]['id'] for t in range(j0, j))))
        # print(len(cosponsor['actions_dates']))
        # 更新网络的邻接矩阵
        # 此处太慢，待解决！
        # for k1 in range(j0, j):
        #     for k2 in range(j0, j):
        #         vote1 = votes_data[k1]
        #         vote2 = votes_data[k2]
        #         net1.add_common_meeting(vote1['id'], vote2['id'])
        #         if votes_data[k1]['vote'] == votes_data[k2]['vote']:
        #             net1.add_same_opinions_meeting(vote1['id'], vote2['id'])
        id_set = set()
        y_id_dict = dict()
        n_id_dict = dict()
        nv_id_dict = dict()
        for k1 in range(j0, j):
            tmp_id = votes_data[k1]['id']
            id_set.add(tmp_id)
        for tmp_id in id_set:
            y_id_dict[tmp_id] = 0
            n_id_dict[tmp_id] = 0
            nv_id_dict[tmp_id] = 0
        for k1 in range(j0, j):
            tmp_vote = votes_data[k1]
            tmp_id = tmp_vote['id']
            if tmp_vote['vote'] == 'Y':
                y_id_dict[tmp_id] += 1
            elif tmp_vote['vote'] == 'N':
                n_id_dict[tmp_id] += 1
            elif tmp_vote['vote'] == 'NV':
                nv_id_dict[tmp_id] += 1
        id_ls = list(id_set)
        id_num = len(id_ls)
        for k1 in range(id_num):
            id1 = id_ls[k1]
            for k2 in range(k1 + 1, id_num):
                id2 = id_ls[k2]
                same_opi = min(y_id_dict[id1], y_id_dict[id2]) + min(n_id_dict[id1], n_id_dict[id2]) \
                           + min(nv_id_dict[id1], nv_id_dict[id2])
                total_opi = min(y_id_dict[id1] + n_id_dict[id1] + nv_id_dict[id1],
                                y_id_dict[id2] + n_id_dict[id2] + nv_id_dict[id2])
                net1.add_same_opinions_meeting(id1, id2, same_opi)
                net1.add_common_meeting(id1, id2, total_opi)

    # 在测试集中预测提案是否通过
    predict = []
    answer = []
    for i in range(n1, n):
        cosponsor = cosponsors_data[i]
        # 该提案的所有提出者id
        sponsors = [cosponsor['sponsor']] + cosponsor['cosponsors']
        sponsors_set = set(sponsors)
        # 该提案的所有投票 votes_data[j0]--votes_data[j]
        j0 = j
        while j < len(votes_data) and votes_data[j]['bill_name'] == cosponsor['bill_id']:
            if not net1.has_node(votes_data[j]['id']):
                member_subclub = None
                if votes_data[j]['id'] in subclub_dict:
                    member_subclub = subclub_dict[votes_data[j]['id']]
                net1.add_node(votes_data[j]['id'], votes_data[j]['group'], votes_data[j]['district'], member_subclub=member_subclub)
            j += 1
        # 预测是否通过
        y1 = 0
        y2 = 0
        for k in range(j0, j):
            vote = votes_data[k]
            if vote['bill_name'] in sponsors_set:
                continue
            for x in sponsors:
                if not net1.has_node(x):
                    member_subclub = None
                    if member_subclub in subclub_dict:
                        member_subclub = subclub_dict[x]
                    net1.add_node(x, member_subclub=member_subclub)
                y1 += net1.get_similarity(vote['id'], x, meeting)
                y2 += 1
        if y2 == 0:
            y = 0
        else:
            y = y1 / y2
        predict.append(y)
        # 计算提案实际是否通过
        y1 = 0
        y2 = 0
        for k in range(j0, j):
            vote = votes_data[k]
            if vote['vote'] == 'Y':
                y1 += 1
            if vote['vote'] != 'NV':
                y2 += 1
        if y2 == 0:
            # 这种情况实际上就是所有人都投弃权票，当成提案未通过
            print('No votes: ' + str(cosponsor))
            y = 0
        else:
            y = y1 / y2
        answer.append(y)

    x = list(range(n-n1))
    # 画两条折线
    plt.plot(x, predict, label='predict')
    plt.plot(x, answer, label='answer')

    # 添加图例和标题
    plt.legend()
    plt.title('Two lines')

    # 显示图像
    plt.show()

    print(predict)
    print(answer)
    cnt = 0
    for i in range(len(predict)):
        if (predict[i] > 0.09) == (answer[i] > 1/2):
            cnt += 1
    print('Accuracy: ' + str(cnt/len(predict)))


if __name__ == "__main__":
    main()
