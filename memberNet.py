class MemberNet:
    def __init__(self):
        # 成员列表，用于从节点编号查找成员id
        self.members_list = []
        # 成员字典，用于从成员id查找节点编号
        self.members_dict = {}
        # 邻接矩阵，adj[i][j]表示i号节点与j号节点的信息，多个二维list记录i,j之间的不同信息
        self.common_meetings = [[0]]
        self.same_opinions_meetings = [[0]]

    def has_node(self, member_id):
        return member_id in self.members_dict

    def add_node(self, member_id):
        # 更新成员列表和成员字典
        self.members_dict[member_id] = len(self.members_list)
        self.members_list.append(member_id)
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

    def get_similarity(self, member_id1, member_id2):
        node1 = self.members_dict[member_id1]
        node2 = self.members_dict[member_id2]
        return self.same_opinions_meetings[node1][node2] / self.common_meetings[node1][node2]