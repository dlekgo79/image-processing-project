import numpy as np
import cv2
import copy

# 전역 변수
firstToggle = True # 초기 설정
flipOn = False #초기값
EdgeOn = False
heart = False
blur = False

xGlob = 0
yGlob = 0
list1 = []
global icon
#아이콘 레이아웃 구성
def place_icons(image, size):

    icon_name = ["clear","change","color","heart"]#icon들의 이름을 배열에 넣었음

    icons= [(i%2, i//2,1,1) for i in range(len(icon_name))]
    icons = np.multiply(icons, size*2)


    for roi,name in zip(icons, icon_name):
        icon = cv2.imread("../images/icon2/%s.png" %name, cv2.IMREAD_COLOR)
        if icon is None: continue
        x,y,w,h = roi
        #print(roi)

        image[y:y+h,x:x+w] = cv2.resize(icon,(60,60))
    return list(icons)


#기능 구현

def onMouse(event,x,y,flags,param):
    global flipOn
    global EdgeOn
    global heart, xGlob, yGlob
    global before
    if event == cv2.EVENT_LBUTTONDOWN:
        for i,(x0,y0,w,h) in enumerate(icons):
            if x0 <= x < x0+w and y0 <= y < y0+h:
                if i == 1:
                    flipOn = not flipOn #True
                elif i == 2:
                    EdgeOn = not EdgeOn
                elif i == 3:
                    heart = not heart

        if(heart):
            #print(x,y)
            xGlob = x
            yGlob = y


#실시간 영상 받아오기
capture = cv2.VideoCapture(0)
if capture.isOpened() == False:
    raise Exception("카메라 연결 안됨")


while cv2.waitKey(30) < 0:
    ret, image_bgr = capture.read()
    image = np.copy(image_bgr)

    if(EdgeOn):
        image1 = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #흑백 사진으로 가지고 옴
        image1 = cv2.GaussianBlur(image1,ksize=(3,3),sigmaX=0) #가우시안 블러를 이용하여 경계선을 흐리게 함
        image_edge = cv2.Canny(image1, 100, 150)#canny edge를 사용하여 경계선 검출
        image = np.stack((image_edge,) * 3, axis=-1)#channel을 변환
        # #전 이미지와 지금 이미지를 비교
        h,w,_ = image.shape
        imgForSave = copy.deepcopy(image) #0번째 저장/ imgForSave에 1 저장 - 깊은 복사
        if not firstToggle: #가장 처음 실행되는 거 뺴고 들어옴
            for i in range(h): #화소에 접근
                for j in range(w):
                    if all(before[i][j] == image[i][j]): #1번과 0번 비교
                        image[i][j] = [0,0,0]
        if firstToggle:
            firstToggle = False

        data = [0,1,0, #모폴로지 적용 data
                 0,1,0,
                 0,1,0]

        mask = np.array(data, np.uint8).reshape(3, 3)
        image = cv2.dilate(image, mask)  # 침식
        image = cv2.erode(image,mask ) #팽창

        for i in range(h-1,0,-1): #끝에서 부터 for문을 돌자
            for j in range(w-1,0,-1):
                 if all(image[i][j] == [255,255,255]):
                    if all(image[i][j - 10] == [255,255,255]):
                        break
                    image[i][j - 1] = [255, 255, 255]

        for i in range(0,h-1,1): #앞에서부터 for문을 돌자
             for j in range(0,w-1,1):
                 if all(image[i][j] == [255,255,255]):
                         if all(image[i][j + 1] == [255,255,255]): #나의 pixel 앞에 흰색이 있으면 stop
                             break
                         image[i][j + 1] = [255, 255, 255]

        #잡음을 제거하기 위해서 침식과 팽창 시도
        # data1 = [0,0,0,1,0,0,0,
        #           0,0,0,1,0,0,0,
        #           1,1,1,1,1,1,1,
        #           0,0,0,1,0,0,0,
        #           0,0,0,1,0,0,0]
        # mask = np.array(data1, np.uint8).reshape(7, 5)
        # image = cv2.erode(image, mask)  # 침식
        # mask = np.array(data, np.uint8).reshape(3, 3)
        # image = cv2.erode(image, mask)  # 침식
        # mask = np.array(data1, np.uint8).reshape(3, 3)
        # image = cv2.dilate(image, mask)

        before = imgForSave #0번째 before에 들어감 before에 1번 들어감
        #
        # for i in range(h):  # 화소에 접근
        #     for j in range(w):
        #         if all(image[i][j] == [0, 0, 0]):
        #             image[i][j] = [0, 255, 255]#배경은 노랑으로
        #         else:
        #             image[i][j] = image_bgr[i][j]#원본으로

    if(flipOn):#True일때만 실행
        image = cv2.flip(image,1)#좌우 반전
    if(heart):
        img1 = cv2.imread('../images/icon2/heart.png')#이미지 붙이기
        rows, cols, channels = img1.shape # 이미지의 가로와 세로를 받기
        a = [xGlob,yGlob]
        list1.append(a)#좌표를 저장
        #print(list1)
        for i in range(len(list1)):
            image[list1[i][1]:list1[i][1] +20, list1[i][0]:list1[i][0] + 20] = cv2.resize(img1, dsize=(20, 20)) #heart 이미지를 (50,50)으로 변경 한 후 image에 삽입

    icons = place_icons(image,(60, 60))
    cv2.imshow("p",image) # 마우스 클릭시 onMouse1 실행8
    cv2.setMouseCallback("p", onMouse)  # 마우스 클릭시 onMouse 실행



capture.release()
cv2.waitKey(0)
