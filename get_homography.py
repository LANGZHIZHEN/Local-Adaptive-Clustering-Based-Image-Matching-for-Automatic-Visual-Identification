import cv2
import numpy as np
import time
from cv2 import cuda
from cv2.xfeatures2d import matchGMS
from server import BEBLID_descriptor_cuda
from server import BEBLID_descriptor
# import pydegensac


def getHomography(h,right_image, template,image_list,pre_index,orb_cuda,matcher):
  
    # detector = cv2.AKAZE_create()
    t1 = time.time()
    kps2,des2 = BEBLID_descriptor_cuda(orb_cuda,right_image)
    # des2 = des2.astype('float32')
    kps, des, left_image = template[0]
    # des = des.astype('float32')
    # index_params = dict(algorithm=1, tree=5)
    # search_params = dict(checks=50)
    # flann = cv2.FlannBasedMatcher(index_params, search_params)
    num = 0
    good_matches = []
    item_matches = []
    template_index = 0
    good_matches_index = 0
    vote = np.zeros(len(template))
    # print("Time1:",time.time()-t1)
    t2 = time.time()
    # print(len(template))
    # matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    if pre_index == -1:
        for i in range(len(template)):
            kps, des, left_image = template[i]
            t4 = time.time()
            matches_all = matcher.match(des, des2)
            t5 = time.time()
            matches_gms = matchGMS(left_image.shape[:2], right_image.shape[:2], kps, kps2, matches_all, withScale=True,
                                withRotation=False, thresholdFactor=5)
            # matches = flann.knnMatch(des1, des2, 2)
            # for m, n in matches:
            #     if m.distance < 0.76 * n.distance:
            #         item_matches.append(m)
            vote[(i-1)%len(template)] += len(matches_gms) * 0.2
            vote[i % len(template)] += len(matches_gms) * 0.6
            vote[(i + 1) % len(template)] += len(matches_gms) * 0.2
            good_matches.append(matches_gms)
        # print("Time2:",time.time()-t2)
        for i in range(len(template)):
            if vote[i] > num:
                num = vote[i]
                kps,des,item = template[i]
                template_index = i
                good_matches_index = i
    else:
        for i in range(3):
            kps, des, left_image = template[(pre_index+i-1)%len(template)]
            t4 = time.time()
            matches_all = matcher.match(des, des2)
            t5 = time.time()
            matches_gms = matchGMS(left_image.shape[:2], right_image.shape[:2], kps, kps2, matches_all, withScale=True,
                                withRotation=False, thresholdFactor=6)
            if i == 0:
                vote[i] += len(matches_gms) * 0.6
                vote[i+1] += len(matches_gms) * 0.4
            if i == 1:
                vote[i-1] += len(matches_gms) * 0.25
                vote[i] += len(matches_gms) * 0.5
                vote[i+1] += len(matches_gms) * 0.25
            if i == 2:
                vote[i-1] += len(matches_gms) * 0.4
                vote[i] += len(matches_gms) * 0.6
            good_matches.append(matches_gms)
        for i in range(3):
            if vote[i] > num:
                num = vote[i]
                kps,des,item = template[(pre_index+i-1)%len(template)]
                template_index = (pre_index+i-1)%len(template)
                good_matches_index = i
    # for i in range(len(template)):
    #     kps, des, left_image = template[i]
    #     t4 = time.time()
    #     matches_all = matcher.match(des, des2)
    #     t5 = time.time()
    #     matches_gms = matchGMS(left_image.shape[:2], right_image.shape[:2], kps, kps2, matches_all, withScale=True,
    #                         withRotation=False, thresholdFactor=6)
    #     # matches = flann.knnMatch(des1, des2, 2)
    #     # for m, n in matches:
    #     #     if m.distance < 0.76 * n.distance:
    #     #         item_matches.append(m)
    #     vote[(i-1)%len(template)] += len(matches_gms) * 0.2
    #     vote[i % len(template)] += len(matches_gms) * 0.6
    #     vote[(i + 1) % len(template)] += len(matches_gms) * 0.2
    #     good_matches.append(matches_gms)
    # # print("Time2:",time.time()-t2)
    # for i in range(len(template)):
    #     if vote[i] > num:
    #         num = vote[i]
    #         kps,des,item = template[i]
    #         template_index = i
    #         good_matches_index = i

    match_result = None
    match_result = cv2.drawMatches(image_list[template_index].image, kps, right_image, kps2, good_matches[good_matches_index], None,
                                   flags=2)
    # end = time.time()
    # print("Time3:" + "\t" + str(end-t1))
    print(len(good_matches[good_matches_index]))
    if len(good_matches[good_matches_index]) >= 30:
        src_points = np.float32([kps[m.queryIdx].pt for m in good_matches[good_matches_index]]).reshape(-1, 2)
        dst_points = np.float32([kps2[m.trainIdx].pt for m in good_matches[good_matches_index]]).reshape(-1, 2)

        # H, mask = pydegensac.findHomography(src_points, dst_points, 3.0)
        H, mask = cv2.findHomography(src_points, dst_points, cv2.RANSAC,4.0)
        sum = 0
        # for i in range(len(mask)):
        #     if mask[i] == True:
        #         sum += 1
        # print("内点率:"+str(sum/len(mask) * 100) + "%"+"特征点数:"+str(len(good_matches[good_matches_index])))
        image_list[template_index].setH(H)
        del good_matches, matches_all, item_matches, kps, kps2
        return template_index,match_result
    else:
        # print("特征点数为"+str(len(good_matches[good_matches_index]))+"没有足够的特征点!")
        del good_matches, matcher,matches_gms,matches_all, item_matches, kps, kps2
        return None, None
