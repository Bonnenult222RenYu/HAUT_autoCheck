import time,json,requests,random,datetime
from campus import CampusCard

def main():
    #定义变量
    success,failure=[],[]
    #sectets字段录入
    phone, password, sckey = [], [], []
    #多人循环录入
    while True:  
        try:
            users = input()
            info = users.split(',')
            phone.append(info[0])
            password.append(info[1])
            sckey.append(info[2])
        except:
            break

    #提交打卡
    for index,value in enumerate(phone):
        print("开始尝试为用户%s打卡"%(value[-4:]))
        count = 0
        while (count <= 3):
            try:
                campus = CampusCard(phone[index], password[index])
                token = campus.user_info["sessionId"]
                userInfo=getUserInfo(token)
                response = checkIn(userInfo,token)
                strTime = getNowTime()
                if response.json()["msg"] == '成功':
                    success.append(userInfo['username'])
                    print(response.text)
                    msg = strTime + userInfo['username']+"打卡成功"
                    if index == 0:
                        result=response
                    break
                else:
                    failure.append(userInfo['username'])
                    print(response.text)
                    msg =  strTime + userInfo['username'] + "打卡异常"
                    count = count + 1
                    if index == 0:
                        result=response
                    if count<=3:
                        print('%s打卡失败，开始第%d次重试...'%(userInfo['username'],count))
                    time.sleep(5)
            except Exception as e:
                print(e.__class__)
                msg = "出现错误"
                failure.append(userInfo['username'])
                break
        print(msg)
        print("-----------------------")
    fail = sorted(set(failure),key=failure.index)
    title = "成功: %s 人,失败: %s 人"%(len(success),len(fail))
    try:
        print('主用户开始微信推送...')
        wechatPush(title,sckey[0],success,fail,result)
    except:
        print("微信推送出错！")

#时间函数
def getNowTime():
    cstTime = (datetime.datetime.utcnow() + datetime.timedelta(hours=8))
    strTime = cstTime.strftime("%H:%M:%S ")
    return strTime

#打卡参数配置函数
def getUserJson(userInfo,token):
    #随机温度(36.2~36.8)
    a=random.uniform(36.2,36.8)
    temperature = round(a, 1)
    return  {
        "businessType": "epmpics",
        "method": "submitUpInfo",
        "jsonData": {
        "deptStr": {
            "deptid": userInfo['classId'],
            "text": userInfo['classDescription']
        },
        #如果你来自其他学校，请自行打卡抓包修改地址字段
        "areaStr": "{\"streetNumber\":\"\",\"street\":\"神农大道\",\"district\":\"天元区\",\"city\":\"株洲市\",\"province\":\"湖南省\",\"town\":\"\",\"pois\":\"湖南工业大学新校区-5栋\",\"lng\":113.11964300000389,\"lat\":27.823026989463784,\"address\":\"天元区神农大道湖南工业大学新校区-5栋\",\"text\":\"湖南省-株洲市\",\"code\":\"\"}",
        "reportdate": round(time.time()*1000),
        "customerid": userInfo['customerId'],
        "deptid": userInfo['classId'],
        "source": "app",
        "templateid": "pneumonia",
        "stuNo": userInfo['stuNo'],
        "username": userInfo['username'],
        "phonenum": "",
        "userid": round(time.time()),
        "updatainfo": [
            {
                "propertyname": "temperature",
                "value": temperature
            },
            {
                "propertyname": "symptom",
                "value": "无症状"
            },
            {
                "propertyname": "isConfirmed",
                "value": "否"
            },
            {
                "propertyname": "isdefinde",
                "value": "否.未隔离"
            },
            {
                "propertyname": "isGoWarningAdress",
                "value": "否"
            },
            {
                "propertyname": "isTouch",
                "value": "否"
            },
            {
                "propertyname": "isFFHasSymptom",
                "value": "没有"
            },
            {
                "propertyname": "isContactFriendIn14",
                "value": "没有"
            },
            {
                "propertyname": "xinqing",
                "value": "健康"
            },
            {
                "propertyname": "bodyzk",
                "value": "是"
            },
            {
                "propertyname": "cxjh",
                "value": "否"
            },
            {
                "propertyname": "isleaveaddress",
                "value": "否"
            },
            {
                "propertyname": "gtjz0511",
                "value": "否"
            },
            {
                "propertyname": "medicalObservation",
                "value": "绿色"
            },
            {
                "propertyname": "ownPhone",
                "value": "13133966922"
            },
            {
                "propertyname": "emergencyContact",
                "value": "梁必柜"
            },
            {
                "propertyname": "mergencyPeoplePhone",
                "value": "13970603959"
            },
            {
                "propertyname": "assistRemark",
                "value": ""
            }
        ],
        "gpsType": 1,
        "token": token
        }
    }    

#信息获取函数
def getUserInfo(token):
    token={'token':token}
    sign_url = "https://reportedh5.17wanxiao.com/api/clock/school/getUserInfo"
    #提交打卡
    response = requests.post(sign_url, data=token)
    print(response.json()['userInfo'])
    return response.json()['userInfo']

#打卡提交函数
def checkIn(userInfo,token):
    sign_url = "https://reportedh5.17wanxiao.com/sass/api/epmpics"
    jsons=getUserJson(userInfo,token)
    #提交打卡
    response = requests.post(sign_url, json=jsons)
    return response

#微信通知
def wechatPush(title,sckey,success,fail,result):    
    strTime = getNowTime()
    page = json.dumps(result.json(), sort_keys=True, indent=4, separators=(',', ': '),ensure_ascii=False)
    content = f"""
`{strTime}` 
#### 打卡成功用户：
`{success}` 
#### 打卡失败用户:
`{fail}`
#### 主用户打卡信息:
```
{page}
```
### 😀[收藏此项目](https://github.com/YooKing/HAUT_autoCheck)

        """
    data = {
            "text":title,
            "desp":content
    }
    scurl='https://sc.ftqq.com/'+sckey+'.send'
    try:
        req = requests.post(scurl,data = data)
        if req.json()["errmsg"] == 'success':
            print("Server酱推送服务成功")
        else:
            print("Server酱推送服务失败")
    except:
        print("微信推送参数错误")

if __name__ == '__main__':
    main()
