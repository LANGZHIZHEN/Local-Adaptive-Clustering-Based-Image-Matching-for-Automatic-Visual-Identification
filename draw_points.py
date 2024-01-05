import math

import cv2
from utils import myPoint

text = "Tag"

def judge(i,j,new_points_info,points_map, points_dis,points_angle):
    dis = getDis(new_points_info[j].cur_point, new_points_info[i].cur_point)
    angle = int(math.atan2(new_points_info[j].cur_point.y - new_points_info[i].cur_point.y,
                           new_points_info[j].cur_point.x - new_points_info[i].cur_point.x) * 180 / math.pi)
    # if new_points_info[j].cur_point.x > new_points_info[i].cur_point.x and new_points_info[j].cur_point.y > \
    #         new_points_info[i].cur_point.y:
    #     if points_map[j][i] != 2:
    #         return False

    # elif new_points_info[j].cur_point.x > new_points_info[i].cur_point.x and new_points_info[j].cur_point.y < \
    #         new_points_info[i].cur_point.y:
    #     if points_map[j][i] != 4:
    #         return False
    # elif new_points_info[j].cur_point.x < new_points_info[i].cur_point.x and new_points_info[j].cur_point.y > \
    #         new_points_info[i].cur_point.y:
    #     if points_map[j][i] != 3:
    #         return False
    # elif new_points_info[j].cur_point.x < new_points_info[i].cur_point.x and new_points_info[j].cur_point.y < \
    #         new_points_info[i].cur_point.y:
    #     if points_map[j][i] != 1:
    #         return False
    if new_points_info[j].cur_point.x > new_points_info[i].cur_point.x:
        if points_map[j,i] != 1:
            return False
    elif new_points_info[j].cur_point.x <= new_points_info[i].cur_point.x:
        if points_map[j,i] != -1:
            return False
    # elif dis < points_dis[i][j] * 0.6 or dis > points_dis[i][j] * 1.4:
    #     return False
    # elif abs(angle - points_angle[i][j]) > 4:
    #     return False
    return True


def getDis(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def calculatePoints(H, points, points_info):
    if H is None:
        return points_info
    for i in range(0, len(points)):
        x = points[i].x
        y = points[i].y
        x2 = points[i].x2
        y2 = points[i].y2
        index = points[i].index
        px = int((H[0, 0] * x + H[0, 1] * y + H[0, 2]) / (H[2, 0] * x + H[2, 1] * y + H[2, 2]))
        py = int((H[1, 0] * x + H[1, 1] * y + H[1, 2]) / (H[2, 0] * x + H[2, 1] * y + H[2, 2]))
        px2 = int((H[0, 0] * x2 + H[0, 1] * y2 + H[0, 2]) / (H[2, 0] * x2 + H[2, 1] * y2 + H[2, 2]))
        py2 = int((H[1, 0] * x2 + H[1, 1] * y2 + H[1, 2]) / (H[2, 0] * x2 + H[2, 1] * y2 + H[2, 2]))
        item = 0
        for j in range(len(points_info)):
            if points_info[j].num == index:
                item = j
        # first match，update cur and pre
        if points_info[item].cur_point.x == x and points_info[item].cur_point.y == y:
            points_info[item].cur_point.x = px
            points_info[item].cur_point.y = py
            points_info[item].cur_point.x2 = px2
            points_info[item].cur_point.y2 = py2
            points_info[item].pre_point.x = px
            points_info[item].pre_point.y = py
            points_info[item].pre_point.x2 = px2
            points_info[item].pre_point.y2 = py2
        dis = getDis(myPoint.Point(px, py,px,py,item), points_info[item].pre_point)
        if dis < 5:
            points_info[item].trust = 1
            points_info[item].cur_point.x = points_info[item].pre_point.x
            points_info[item].cur_point.y = points_info[item].pre_point.y
            points_info[item].cur_point.x2 = points_info[item].pre_point.x2
            points_info[item].cur_point.y2 = points_info[item].pre_point.y2
        else:
            points_info[item].trust = 0
            points_info[item].cur_point.x = px
            points_info[item].cur_point.y = py
            points_info[item].cur_point.x2 = px2
            points_info[item].cur_point.y2 = py2
        points_info[item].pre_point.x = points_info[item].cur_point.x
        points_info[item].pre_point.y = points_info[item].cur_point.y
        points_info[item].pre_point.x2 = points_info[item].cur_point.x2
        points_info[item].pre_point.y2 = points_info[item].cur_point.y2
    return points_info


def drawPoints(image, my_template, points_info, points_map, points_dis,points_angle,label_points):
    width = image.image.shape[1]
    height = image.image.shape[0]
    new_points_info = calculatePoints(my_template.H, my_template.points, points_info)
    good_num = []
    bad_num = []
    receive_num = []
    good_result = []
    # print(len(my_template.points))
    for i in range(0, len(my_template.points)):
        receive_num.append(my_template.points[i].index)
        # if new_points_info[i].cur_point.x < 0 or new_points_info[i].cur_point.x >= image.rows or new_points_info[i].cur_point.y < 0 or new_points_info[i].cur_point.y >= image.cols:
        #     continue
        # else:
        #     receive_num.append(my_template.points[i].index)
        # elif new_points_info[i].trust == 0 :
        #     bad_num.append(my_template.points[i].index)
        # else:
        #     good_num.append(my_template.points[i].index)
        #     receive_num.append(my_template.points[i].index)
    # for m in range(0, len(bad_num)):
    #     j = bad_num[m]
    #     flag = True
    #     for n in range(0, len(good_num)):
    #         i = good_num[n]
    #         if not judge(i, j, new_points_info, points_map, points_dis, points_angle):
    #             flag = False
    #             break
    #     if flag:
    #         receive_num.append(j)
    for j in receive_num:
        x2 = new_points_info[j].cur_point.x2
        y2 = new_points_info[j].cur_point.y2
        w_2= label_points[j].w
        h_2 = label_points[j].h
        w = (x2-new_points_info[j].cur_point.x)
        h = (y2-new_points_info[j].cur_point.y)
        # print("befroe:"+str(w_2/width)+";after:"+str(w))
        # print("befroe:"+str(h_2/height)+";after:"+str(h))
        note = label_points[j].note
        name = label_points[j].name
        good_result.append((j, new_points_info[j].cur_point.y/height, new_points_info[j].cur_point.x/width,(w/width,h/height),name,note))
    return good_result
