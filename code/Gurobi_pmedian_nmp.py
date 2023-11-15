import pickle
from gurobipy import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import time

def gurobi_solver_pMedian(users, facilities, C, P):
    N = users.size()[0]
    M = facilities.size()[0]

    model = Model('pmedian')
    model.setParam('OutputFlag', False)
    model.setParam('MIPFocus', 1)

    x = {}
    y = {}

    # Add Client Decision Variables and Service Decision Variables
    for i in range(M):
        y[i] = model.addVar(vtype=GRB.INTEGER,lb=0, ub=1, name="y(%s)" % i)
        for j in range(N):
            x[i, j] = model.addVar(vtype=GRB.INTEGER,lb=0, ub=1, name="x(%s, %s)" % (i, j))

    #     Add Constraints
    model.addConstr(sum(y[i] for i in range(M)) == P)
    for j in range(N):
        model.addConstr(sum(x[i, j] for i in range(M)) == 1)
    for i in range(M):
        for j in range(N):
            model.addConstr(x[i, j] <= y[i])

    model.update()
    model.setObjective(quicksum(C[i, j] * x[i, j] for i in range(M) for j in range(N)),GRB.MAXIMIZE)
    model.optimize()

    x_result = np.zeros((M, N))
    y_result = np.zeros(N)
    for i in range(M):
        y_result[i] = y[i].X
        # y_result[i] = y[i].solution_value()
        for j in range(N):
            x_result[i, j] = x[i, j].X
    obj = model.objVal
    return x_result, y_result, obj

def plot_users_facilities(users, facilities,y_result,r):
    plt.subplots(figsize=(16, 16))
    plt.scatter(users[:, 0], users[:, 1], color='lightblue', label='Users',s=1)
    plt.scatter(facilities[:, 0], facilities[:, 1], color='green', label='Facilities',s=1)
    # 根据 y_result 中的值，绘制被选中的设施点
    selected_indices = np.where(y_result == 1)[0]
    selected_facilities = facilities[selected_indices]
    plt.scatter(selected_facilities[:, 0], selected_facilities[:, 1], color='red', label='Selected Facilities',s=3)
    for facility in selected_facilities:
        circle = Circle(facility, radius=r, color='red', fill=False)
        plt.gca().add_patch(circle)

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Cainiao Station Spatial Optimization Solution by Gurobi')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == '__main__':

    n = 2000
    m = 20
    p = 8

    objs = []

    start_time = time.time()
    # filename = r"E:\pycharm_professional\cainiao\data\pmediam_nmp_100_20_8.pkl"
    filename = r"E:\pycharm_professional\cainiao\data\pmediam_nmp_2000_20_8.pkl"
    # filename = r"E:\pycharm_professional\cainiao\data\MCLP_100_1000_test_1_Normalization.pkl"
    # filename = r"E:\pycharm_professional\cainiao\data\pMedian_nmp_28140_3000_1000.pkl"
    # filename = r"E:\pycharm_professional\cainiao\data\pmedian_nmp_28140_1500_1000.pkl"
    # filename = r"E:\pycharm_professional\cainiao\data\pmedian_nmp_28140_1500_25.pkl"
    # filename = r"E:\pycharm_professional\cainiao\data\pmedian_nmp_28140_100_25.pkl"


    with open(filename, 'rb') as f:
        datas = pickle.load(f)
        num_sample = len(datas)

    for i in range(len(datas)):
        data = datas[i]
        users = data["users"]
        facilities = data["facilities"]
        demand = data["demand"]
        r = data["r"]
        dist = (facilities[:, None, :] - users[None, :, :]).norm(p=2, dim=-1)
        dist = 1 / (dist + 1)
        weighted_dist = demand[None, :] * dist
        dists = weighted_dist.detach().numpy()

        x_result, y_result, obj = gurobi_solver_pMedian(users, facilities, dists, p)
        plot_users_facilities(users, facilities, y_result,r)
        selected_indices = np.where(y_result == 1)[0]
        selected_facilities = facilities[selected_indices]
        selected_facility_indices = selected_indices.tolist()
        objs.append(obj)
        print(f"instance {i + 1} has been finished")

    end_time = time.time() - start_time
    average_obj = np.mean(objs)
    print(f"or-tools, {n}-{m}-{p}")
    print(f"The number of instances is: {num_sample}")
    print(f"The total solution time is: {end_time}")
    print(f"The average solution time is: {end_time / num_sample}")
    print(f"The average objective is: {average_obj}")