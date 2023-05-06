class MemberNet:
    def __init__(self):
        # 成员列表，用于从节点编号查找成员id
        self.members_list = []
        # 成员字典，用于从成员id查找节点编号
        self.members_dict = {}
        # 成员的其他信息，用于从节点编号查找成员的该项信息
        self.members_group = []
        self.members_district = []
        self.members_subclub = []  # 这个list中的元素是dict，键值是meeting号
        # 邻接矩阵，adj[i][j]表示i号节点与j号节点的信息，多个二维list记录i,j之间的不同信息
        self.common_meetings = [[0]]
        self.same_opinions_meetings = [[0]]

    def has_node(self, member_id):
        return member_id in self.members_dict

    def add_node(self, member_id, member_group=None, member_district=None, member_subclub=None):
        # 更新成员列表和成员字典
        self.members_dict[member_id] = len(self.members_list)
        self.members_list.append(member_id)
        # 更新成员的其他信息列表
        self.members_group.append(member_group)
        self.members_district.append(member_district)
        self.members_subclub.append(member_subclub)
        # 扩展邻接矩阵
        for i in range(len(self.common_meetings)):
            self.common_meetings[i].append(0)
        for i in range(len(self.same_opinions_meetings)):
            self.same_opinions_meetings[i].append(0)
        self.common_meetings.append([0 for _ in range(len(self.common_meetings[0]))])
        self.same_opinions_meetings.append([0 for _ in range(len(self.same_opinions_meetings[0]))])

    def add_common_meeting(self, member_id1, member_id2, total_opi):
        node1 = self.members_dict[member_id1]
        node2 = self.members_dict[member_id2]
        self.common_meetings[node1][node2] += total_opi

    def add_same_opinions_meeting(self, member_id1, member_id2, same_opi):
        node1 = self.members_dict[member_id1]
        node2 = self.members_dict[member_id2]
        self.same_opinions_meetings[node1][node2] += same_opi

    def get_similarity(self, member_id1, member_id2, meeting=None):
        node1 = self.members_dict[member_id1]
        node2 = self.members_dict[member_id2]
        y1 = 0
        y2 = 0
        if self.common_meetings[node1][node2] > 0:
            y1 += self.same_opinions_meetings[node1][node2] / self.common_meetings[node1][node2]
            y2 += 0.85
        if self.members_group[node1] is not None:
            if self.members_group[node1] == self.members_group[node2]:
                y1 += 0.05
            y2 += 0.05
        if self.members_district[node1] is not None:
            if self.members_district[node1] == self.members_district[node2]:
                y1 += 0.05
            y2 += 0.05
        if meeting is not None and self.members_subclub[node1] is not None and self.members_subclub[node2] is not None:
            if meeting in self.members_subclub[node1] and meeting in self.members_subclub[node2]:
                if self.members_subclub[node1][meeting] == self.members_subclub[node2][meeting]:
                    y1 += 0.05
                y2 += 0.05
        if y2 == 0:
            print('################')
            print(member_id1)
            print(member_id2)
            print(meeting)
            print('################')
            return 0
        else:
            return y1 / y2
