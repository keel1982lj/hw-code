from Road import Road
import numpy as np
import math
import random



class Map(object):
    def __init__(self, crosses=None, roads=None, time=0, cars=None, map_path=None):
        self.mapRoad = None     # 各个节点之间的路
        self.crosses = crosses
        self.roads = roads
        self.time = time
        self.cars = cars
        self.initRoad()
        self.map_path = map_path
        self.mapValue = None # self.Newmap()  # 各个节点之间的费用矩阵
        self.isNew=[False for i in range(roads.__len__())]

    def map_Dijkstra(self, fr):
        if not self.isNew[fr]:
            if fr%2==0:
                self.Newmap(model=True)
            else:
                self.Newmap(model=False)
            dis = {}  # 当前节点距离每个节点的距离
            visited = []
            _min_dis = None
            _min_dis_point = None

            # 先初始化
            for i in range(len(self.mapValue)):  # map指的是各个路口到各个路口的权值矩阵
                dis[i] = [self.mapValue[fr][i], []]
            for i in range(len(dis)):
                sort_dis = sorted(dis.items(), key=lambda item: item[1][0])  # 找到dis中距离起始点距离最小的点
                for p, d in sort_dis:
                    if p not in visited:
                        _min_dis_point = p
                        _min_dis = d[0]
                        visited.append(p)
                        break
                for j in range(len(self.mapValue)):
                    if self.mapValue[_min_dis_point][j] < float("inf"):
                        update = _min_dis + self.mapValue[_min_dis_point][j]
                        if dis[j][0] > update:
                            dis[j][0] = update
                            dis[j][1] = dis[_min_dis_point][1][:]
                            dis[j][1].append(_min_dis_point)
            for j in range(self.crosses.__len__()):
                if not j == fr:
                    dis[j][1].insert(0, fr)
                    dis[j][1].extend([j])
                    self.map_path[fr][j] = dis[j][1]

    # 初始化地图
    def Newmap(self, model=True):
        value = np.zeros([self.crosses.__len__(), self.crosses.__len__()])
        for i in range(self.crosses.__len__()):
            for j in range(self.crosses.__len__()):
                value[i][j] = float("inf")
        for i in range(self.roads.__len__()):
            road = self.roads[i]
            count_car = 1
            velocity = 1
            minv = 10
            count = 0.1
            # 获取这条路上的车数量，和他们速度平均值
            for i in range(road.channel.__len__()):
                for j in range(road.channel[0].__len__()):
                    if not road.channel[i][j] == 0:
                        count = count +1
                        velocity = velocity + road.channel[i][j].spd
                        if road.channel[i][j].spd < minv:
                            minv = road.channel[i][j].spd  # 道路中速度最小值
                        count_car = count_car + 1
            velocity = velocity // count_car
            # v = 100 * road.lth // road.spd // pow(road.chlnum, 0.2) // pow(minv, 2) // pow(velocity,
            #                                                                      2) + 10 * road.lth // road.spd - math.log(max(0.0001, 0.5-count_car/(count/road.chlnum)))# 大体上估计的一个公式
            if model:
                v = 100 * road.lth // road.spd//road.chlnum//pow(minv, 2)//pow(velocity, 2) + 10*road.lth//road.spd
            else:
                v = 100 * road.lth // road.spd//road.chlnum//pow(minv, 2)//pow(velocity, 2) + 10*road.lth//road.spd
            value[road.fr][road.to] = v
        self.mapValue = value

    # 初始化地图中的路径矩阵
    def initRoad(self):
        roadmat = [[0 for i in range(self.crosses.__len__())] for j in range(self.crosses.__len__())]
        for i in range(self.roads.__len__()):
            road = self.roads[i]
            roadmat[road.fr][road.to] = road
        self.mapRoad = roadmat

    # 车跑
    def car_run(self, cross_mapid, nowroad=None, nextroad=None, nowchannel=None, car=None, dao=False):

        dis_cross = 0
        if not nowchannel == None:    # 不是从无限车库中跳出来的
            index = nowchannel.index(car)
            dis_cross = nowchannel.__len__()-1-index    # 到最后的距离

            # 不会跑出本条路
            if car.spd <= dis_cross:     # 第二个条件？？？？
                loc = index + car.spd
                for i in range(index+1, loc+1)[::-1]:
                    if not nowchannel[i] == 0:
                        loc = loc-1
                nowchannel[index], nowchannel[loc] = nowchannel[loc], nowchannel[index]
                car.time = car.time+1
                newspeed = min(nowroad.spd, car.speed)
                if(loc<nowchannel.__len__() - 1):
                    if not nowchannel[loc+1] == 0:
                        car.spd = min(newspeed, nowchannel[loc+1].spd)
                car.spd = newspeed
            # 有可能会到下一条路时
            elif car.spd > dis_cross and min(nextroad.spd, car.spd)-dis_cross > 0 and not dao:
                # car.map = self.Newmap()
                # car.Dijkstra(isInit=False)
                # 考虑如果当前路被堵死了
                loc_ = nowchannel.__len__()-1
                for i in range(index+1, loc_+1)[::-1]:
                    if not nowchannel[i] == 0:
                        loc_ = loc_-1
                if not loc_==nowchannel.__len__()-1:   #说明前路堵住了
                    nowchannel[index], nowchannel[loc_] = nowchannel[loc_], nowchannel[index]
                    car.time = car.time + 1
                    newspeed = min(nowroad.spd, car.speed)
                    if (loc_ < nowchannel.__len__() - 1):
                        if not nowchannel[loc_ + 1] == 0:
                            car.spd = min(newspeed, nowchannel[loc_ + 1].spd)
                    car.spd = newspeed
                    # car.map = self.mapValue
                    # car.Dijkstra(isInit=False)
                else:     # 前路畅通
                    if car.to == cross_mapid:
                        print("到站")
                        car.realroad.append(cross_mapid)
                        car.isloc = True
                        nowchannel[index] = 0    # 到站
                    else:
                        loc = [0, min(nextroad.spd, car.spd)-dis_cross-1]       # 下一条路中可以停车的位置
                        for channelid in range(nextroad.chlnum):
                            for i in range(min(nextroad.spd, car.spd) - dis_cross)[::-1]:
                                if not nextroad.channel[channelid][i] == 0:
                                    loc = [channelid, i-1]
                            if loc[1] >=0:
                                break
                            # loc = [channelid, min(nextroad.spd, car.spd) - dis_cross - 1]
                        if loc[1] >=0:
                            print(loc)
                            nextroad.channel[loc[0]][loc[1]] = nowchannel[index]
                            nowchannel[index] = 0
                            car.time = car.time + 1     # 车上的表更改时间
                            car.fr = nextroad.to
                            # del (car.planpath[0])
                            # car.realpath.append(cross_mapid)
                            car.realroad.append(nowroad.id)

                            newspeed = min(nextroad.spd, car.speed)
                            nextroad_car = nextroad.channel[loc[0]][loc[1] + 1]
                            if not nextroad_car == 0:
                                car.spd = min(newspeed, nextroad_car.spd)
                            car.spd = newspeed
                        else:
                            car.time = car.time+1
            # 其他情况
            else:
                # 考虑如果当前路被堵死了
                loc_ = nowchannel.__len__() - 1
                for i in range(index+1, loc_ + 1)[::-1]:
                    if not nowchannel[i] == 0:
                        loc_ = loc_ - 1
                if not loc_ == nowchannel.__len__() - 1:  # 说明前路堵住了
                    nowchannel[index], nowchannel[loc_] = nowchannel[loc_], nowchannel[index]
                    car.time = car.time + 1
                    newspeed = min(nowroad.spd, car.speed)
                    if (loc_ < nowchannel.__len__() - 1):
                        if not nowchannel[loc_ + 1] == 0:
                            car.spd = min(newspeed, nowchannel[loc_ + 1].spd)
                    car.spd = newspeed
                    # if int(car.id) % 2 == 0:
                    #     car.map = self.mapValue
                    #     car.Dijkstra(isInit=False)
                else:
                    if car.to == cross_mapid:
                        print("2到站")
                        car.realroad.append(nowroad.id)
                        car.isloc = True
                        nowchannel[index] = 0
                    else:
                        nowchannel[index], nowchannel[loc_] = nowchannel[loc_], nowchannel[index]
                        car.time = car.time + 1
                        newspeed = min(nowroad.spd, car.speed)
                        car.spd = newspeed
        else:  # 从无限车库中出来的
            if 0 not in nextroad.channel[:][0]:
                car.time = car.time+1
                car.plt = car.plt+ (15-car.spd)*2
                # print("出不来了")
                # if car.id % 7 == 0:
                #     print("出不来，Di了")
                self.map_Dijkstra(cross_mapid)
            else:
                loc = [0, min(nextroad.spd, car.spd) - dis_cross - 1]  # 下一条路中可以停车的位置
                for channelid in range(nextroad.chlnum):
                    for i in range(min(nextroad.spd, car.spd - dis_cross))[::-1]:    # 此处有疑问，到下一条车道的时候最大只能是5吗？
                        if not nextroad.channel[channelid][i] == 0:
                            loc = [channelid, i - 1]
                    if loc[1] >= 0:
                        break
                    # loc = [channelid, min(nextroad.spd, car.spd) - dis_cross - 1]
                if loc[1] >= 0:
                    nextroad.channel[loc[0]][loc[1]] = car    # 进入下一条路
                    car.time = car.time + 1  # 车上的表更改时间
                    car.plt = float("inf")
                    car.fr = nextroad.to
                    # car.realpath.append(cross_mapid)
                    newspeed = min(car.speed, nextroad.spd)
                    nextroad_car = nextroad.channel[loc[0]][loc[1]+1]
                    if not nextroad_car == 0:
                        car.spd = min(newspeed, nextroad_car.spd)
                    car.spd = newspeed
                    car.realplt = self.time
                else:
                    car.realplt = car.realplt
    # 下一时刻
    def next(self):
        # self.mapValue = self.Newmap()
        # 根据路口升序依次调度
        for i in range(self.crosses.__len__()):
            cross = self.crosses[i].mapid     # 当前所关注的路口
            roadIds = self.crosses[i].rids      # 这个路口所连接的路的id号
            road_cross_list = {}
            cross_road_list = {}
            for road_ in self.roads:
                if road_.id == roadIds[0]:
                    if road_.to == cross:
                        road_cross_list[0] = road_
                    else:
                        cross_road_list[road_.id] = 0
                elif road_.id == roadIds[1]:
                    if road_.to == cross:
                        road_cross_list[1] = road_
                    else:
                        cross_road_list[road_.id] = 1
                elif road_.id == roadIds[2]:
                    if road_.to == cross:
                        road_cross_list[2] = road_
                    else:
                        cross_road_list[road_.id] = 2
                elif road_.id == roadIds[3]:
                    if road_.to == cross:
                        road_cross_list[3] = road_
                    else:
                        cross_road_list[road_.id] = 3      # 通过该循环将该路口所连接的道路存入  road_cross_list 和 cross_road_list当中
                for i in range(road_.chlnum):
                    if road_.channel[i].count(0) < 1 :
                        for j in range(road_.lth):
                            if not road_.channel[i][j].to == cross:
                                road_car = road_.channel[i][j]
                                if not road_car == 0:
                                    road_car.plt = self.time + [1, 3, 5, 9, 14][self.time%5] # random.choices([1, 2, 5, 9, 14])[0]  # 参数是拍脑袋想的
                                    road_car.realroad=[]
                                    road_car.fr=road_car.realfr

                                    self.map_Dijkstra(road_car.fr)

                                    road_.channel[i][j] = 0


            v = [True, True, True]
            while True:
                # 直行
                v[0] = True
                for key, road_ in sorted(road_cross_list.items(), key=lambda item: item[1].id):   # 按照id的升序来调度车辆
                    for i in range(road_.lth)[::-1]:
                        for j in range(road_.chlnum):
                            road_car = road_.channel[j][i]
                            if not road_car == 0:
                                if road_car.time <= self.time and len(set(road_.channel[j][i+1:]))<= 1:
                                    # if self.time%7 ==0:
                                    #     oldpath = road_car.planpath
                                    #     road_car.map = self.Newmap()
                                    #     road_car.Dijkstra(isInit=False)
                                    #     if len(road_car.planpath)>=3:
                                    #         if road_car.planpath[2] ==road_.fr:
                                    #             road_car.planpath = oldpath
                                    if road_car.spd+i+1>road_.lth:
                                        v[0] = True

                                        nextroad_ = road_
                                        planpath_car = self.map_path[road_car.fr][road_car.to]
                                        if planpath_car.__len__() >= 2:
                                            nextroad_ = self.mapRoad[planpath_car[0]][
                                                planpath_car[1]]
                                        # print("直行")
                                        if nextroad_ == road_:

                                                self.car_run(nowroad=road_, cross_mapid= cross, nextroad = nextroad_, nowchannel=road_.channel[j], car =road_car, dao=True)
                                        elif cross_road_list[nextroad_.id] == (key + 2) % 4:
                                            self.car_run(nowroad=road_, cross_mapid=cross, nextroad=nextroad_,
                                                         nowchannel=road_.channel[j], car=road_car)
                                    else:
                                        v[0] = False
                                else:
                                    v[0] = False
                            if i == 0 and j == road_.chlnum-1:
                                v[0] = False
                # 左拐
                v[1] = True
                for key, road_ in sorted(road_cross_list.items(), key=lambda item: item[1].id):   # 按照id的升序来调度车辆
                    for i in range(road_.lth)[::-1]:
                        for j in range(road_.chlnum):
                            road_car = road_.channel[j][i]
                            if not road_car == 0:
                                if road_car.time<=self.time and len(set(road_.channel[j][i+1:])) <= 1:
                                    # if self.time% 6 ==0:
                                    #     oldpath = road_car.planpath
                                    #     road_car.map = self.Newmap()
                                    #     road_car.Dijkstra(isInit=False)
                                    #     if len(road_car.planpath) >= 3:
                                    #         if road_car.planpath[2] == road_.fr:
                                    #             road_car.planpath = oldpath
                                    if road_car.spd + i + 1 > road_.lth:
                                        v[1] = True
                                        nextroad_ = road_
                                        planpath_car = self.map_path[road_car.fr][road_car.to]
                                        if planpath_car.__len__() >= 2:
                                            nextroad_ = self.mapRoad[planpath_car[0]][
                                                planpath_car[1]]
                                        # print("左")
                                        if nextroad_==road_:
                                                self.car_run(nowroad=road_, cross_mapid= cross, nextroad = nextroad_, nowchannel=road_.channel[j], car =road_.channel[j][i], dao=True)
                                        elif cross_road_list[nextroad_.id] == (key + 1) % 4:
                                            self.car_run(nowroad=road_, cross_mapid=cross, nextroad=nextroad_,
                                                         nowchannel=road_.channel[j], car=road_car)
                                    else:
                                        v[1] = False
                                else:
                                    v[1] = False
                            if i ==0 and j ==road_.chlnum-1:
                                v[1] = False
                # 右拐
                v[2] = True
                for key, road_ in sorted(road_cross_list.items(), key=lambda item: item[1].id):   # 按照id的升序来调度车辆
                    for i in range(road_.lth)[::-1]:
                        for j in range(road_.chlnum):
                            road_car = road_.channel[j][i]
                            if not road_car == 0:
                                if road_car.time <= self.time and len(set(road_.channel[j][i+1:])) <= 1:
                                    # if self.time %5 ==0:
                                    #     oldpath = road_car.planpath
                                    #     road_car.map = self.Newmap()
                                    #     road_car.Dijkstra(isInit=False)
                                    #     if len(road_car.planpath) >= 3:
                                    #         if road_car.planpath[2] == road_.fr:
                                    #             road_car.planpath = oldpath
                                    if road_car.spd + i + 1 > road_.lth:
                                        v[2] = True
                                        nextroad_ = road_
                                        planpath_car = self.map_path[road_car.fr][road_car.to]
                                        if planpath_car.__len__() >= 2:
                                            nextroad_ = self.mapRoad[planpath_car[0]][
                                                planpath_car[1]]
                                        # print("右拐")
                                        if nextroad_==road_:
                                                self.car_run(nowroad=road_, cross_mapid= cross, nextroad = nextroad_, nowchannel=road_.channel[j], car =road_.channel[j][i], dao=True)
                                        elif cross_road_list[nextroad_.id] == (key + 3) % 4:
                                            self.car_run(nowroad=road_, cross_mapid=cross, nextroad=nextroad_,
                                                         nowchannel=road_.channel[j], car=road_car)
                                else:
                                    v[2] = False
                            else:
                                v[2] = False
                            if i == 0 and j ==road_.chlnum-1:
                                v[2] = False
                if not(v[0] or v[1] or v[2]):
                    break

            # 把剩下的不能过路口的车辆跑过去
            for key, road_ in sorted(road_cross_list.items(), key=lambda item: item[1].id):
                for i in range(road_.lth)[::-1]:
                    for j in range(road_.chlnum):
                        road_car = road_.channel[j][i]
                        if not road_car == 0:
                            if road_car.time <= self.time:
                                    nextroad_ = Road(-1, 10, -2, 1, 0, 0)
                                    self.car_run(nowroad=road_, cross_mapid=cross, nextroad=nextroad_,
                                                 nowchannel=road_.channel[j], car=road_car)

            for car in self.cars:      # 上路
                if car.plt <= self.time and car.fr == cross:
                    # if self.time % 5 == 0:
                    #     car.map = self.Newmap()
                    #     car.Dijkstra()

                    planpath_car = self.map_path[car.fr][car.to]

                    nextroad_ = self.mapRoad[planpath_car[0]][planpath_car[1]]

                    # nextroad_list = [i for i in self.mapRoad[car.fr] if not i == 0]


                    #if 0 not in nextroad_.channel[:][0]:

                    #     car.time = car.time + 1
                    #     car.plt = car.plt + (15-car.spd)*2
                    #     if car.id % 7 == 0:
                    #         print("出不来，Di了")
                    #         self.map_Dijkstra(cross)
                    # 随机上路
                    # for nextroad_ in nextroad_list:
                    # print(nextroad_list)
                    # self.car_run(cross_mapid=cross, nextroad=random.choices(nextroad_list)[0], car=car)
                    self.car_run(cross_mapid=cross, nextroad=nextroad_, car=car)

        self.time = self.time+1

    # 根据车过的路口——》车过的路
    def cross_road(self):
        for car in self.cars:
            for i in range(car.realpath.__len__()):
                if car.realpath.__len__()-1-i >= 1:   # 判断到还没有到最后一个点
                    car.realroad.append((self.mapRoad[car.realpath[i]][car.realpath[i+1]]).id)






# if __name__ == "__main__":
#     car_data = pd.read_csv("car.txt")
#     cross_data = pd.read_csv("cross.txt")
#     road_data = pd.read_csv("road.txt")
#     car_list = []
#     cross_list = []
#     road_list = []
#     # 将车都存入一个列表
#     for i in range(car_data.__len__()):
#         car = car_data.loc[i]
#         car_list.append(Car(id=int(car[0][1:]), fr=int(car[1])-1, to=int(car[2])-1, speed=int(car[3]), plt=int(car[4][:-1])))
#     # 将路口存入一个列表
#     for i in range(cross_data.__len__() - 1):
#         cross = cross_data.loc[i]
#         cross_list.append(Cross(id=int(car[0][1:]), rid1=int(cross[1]), rid2=int(cross[2]), rid3=int(cross[3]), rid4=int(cross[4][:-1]), mapid=i))
#     # 将路存入一个列表
#     for i in range(road_data.__len__()):
#         road = road_data.loc[i]
#         road_list.append(Road(id=int(road[0][1:]), lth=int(road[1]), spd=int(road[2]), chlnum=int(road[3]), fr=int(road[4])-1, to=int(road[5])-1))
#         if int(road[6][:-1]) == 1:    # 如果是双向的就再加上
#             road_list.append(
#                 Road(id=int(road[0][1:]), lth=int(road[1]), spd=int(road[2]), chlnum=int(road[3]), fr=int(road[5])-1,
#                      to=int(road[4])-1))
#
#     for car in car_list:    # 初始化车辆
#         car.map = initmap(cross=cross_list, roads=road_list)
#         car.Dijkstra()
#
#     ti = 1
#     while isArr(car_list) == False:
#         mmap = Map(crosses=cross_list, cars=car_list, roads=road_list, time=ti)
#         mmap.next()
#         ti = ti+1
#         print(ti)
#
#     for car in car_list:
#         print("出结果了！")
#         print(car.realpath)

    # map = [[float("inf")] * 6 for i in range(6)]
    # for i in range(6):
    #     map[i][i]=0
    # map[0][1]=1
    # map[0][2]=12
    # map[1][2]=9
    # map[1][3]=3
    # map[2][4]=5
    # map[3][2]=4
    # map[3][4]=13
    # map[3][5]=15
    # map[4][5]=4
    # cross1 = Cross(id=0, mapid=0)
    # cross2 = Cross(id=1, mapid=5)
    # car = Car(id=0, fr=0, to=5, speed=2, plt=None, map=map)
    # car.Dijkstra()
    # print(car.planpath)


