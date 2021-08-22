import re
import openpyxl

import API1
from API1 import user


def evalAges(user, dictObj):
    ages = ''
    birthYear = user['infor']['birthYear']
    if 1920 <= birthYear <= 1955:
        ages = '>65'
    elif 1956 <= birthYear <= 1965:
        ages = '55-65'
    elif 1966 <= birthYear <= 1975:
        ages = '45-54'
    elif 1976 <= birthYear <= 1985:
        ages = '35-44'
    elif 1986 <= birthYear <= 1990:
        ages = '30-34'
    elif 1991 <= birthYear <= 1997:
        ages = '23-29'
    elif 1998 <= birthYear <= 2002:
        ages = '18-22'
    elif 2003 <= birthYear <= 2020:
        ages = '<18'
    try:
        indicatorAges = user['infor']['indicator']['ages'][0] if len(user['infor']['indicator']['ages']) > 0 else None
        if indicatorAges == '1920-1955':
            ages = '>65'
        elif indicatorAges == '1956-1965':
            ages = '55-65'
        elif indicatorAges == '1966-1975':
            ages = '45-54'
        elif indicatorAges == '1976-1985':
            ages = '35-44'
        elif indicatorAges == '1986-1990':
            ages = '30-34'
        elif indicatorAges == '1991-1998':
            ages = '23-29'
        elif indicatorAges == '1998-2002':
            ages = '18-22'
        elif indicatorAges == '2003-2008':
            ages = '<18'
    except KeyError:
        pass

    try:
        predictionAges = user['infor']['prediction']['ages']['scores']
        maxProbabilityAges = 0
        for age in predictionAges:
            if predictionAges[age] > maxProbabilityAges:
                maxProbabilityAges = predictionAges[age]
                ages = age
    except KeyError:
        pass

    for age in dictObj['Tuổi']:
        strCheck = re.findall('\(\S*', age)[0][1:-1]
        if ages == strCheck:
            dictObj['Tuổi'][age] = '1'


def evalRelationship(user, dictObj):
    relation = ''
    relationship = user['infor']['relationship']
    if relationship == 'Góa' and relationship == 'Đã ly hôn':
        relation = 'Li thân/Li hôn/Đơn thân'
    elif relationship == 'Hẹn hò' and relationship == 'Đã đính hôn' and relationship == 'Chung sống':
        relation = 'Hẹn hò'
    elif relationship == 'Đã kết hôn':
        relation = 'Đã kết hôn'
    elif relationship == 'Độc thân' and relationship == 'Tìm hiểu':
        relation = 'Độc thân'

    try:
        indicatorRelations = user['infor']['indicator']['relations'][0] if len(
            user['infor']['indicator']['relations']) > 0 else None
        listValues = ['Hẹn hò', 'Li thân/Li hôn/Đơn thân', 'Đã kết hôn', 'Độc thân']
        relation = indicatorRelations if indicatorRelations in listValues else relation
    except KeyError:
        pass

    try:
        predictionRelations = user['infor']['prediction']['relations']['scores']
        maxProbabilityRel = 0
        for rel in predictionRelations:
            if predictionRelations[rel] > maxProbabilityRel:
                maxProbabilityRel = predictionRelations[rel]
                relation = rel
        relation = 'Độc thân' if relation == 'single' else 'Hẹn hò' if relation == 'in_relationship' \
            else 'Li thân/Li hôn/Đơn thân' if relation == 'broken' else 'Đã kết hôn'
    except KeyError:
        pass

    for rel in dictObj['Tình trạng hôn nhân']:
        if relation == rel:
            dictObj['Tình trạng hôn nhân'][rel] = '1'


def evalGender(user, dicObj):
    gender = user['infor']['gender']
    gender = 'Nam' if gender == 'male' else 'Nữ' if gender == 'female' else 'Khác'
    for sex in dicObj['Giới tính']:
        if sex == gender:
            dicObj['Giới tính'][sex] = '1'


def evalChild(user, dicObj):
    hasChild = 0
    try:
        hasChild = user['infor']['indicator']['hasChild']
        dicObj['Gia đình']['Đã có con hay chưa'] = '1' if hasChild == 1 else ''
    except KeyError:
        pass
    try:
        hasChild = user['infor']['prediction']['childs']['scores']['has_child']
        dicObj['Gia đình']['Đã có con hay chưa'] = '1' if hasChild > 0.6 else ''
    except KeyError:
        pass


def evalJob(user, dicObj, Sheet):
    predictionJob = ''
    listNameGroup = []
    listDescriptionGroup = []
    listPosition = []
    try:
        listPosition = [pos['position'].lower() for pos in user['infor']['works'] if pos['position'] is not None]
    except:
        pass
    try:
        listNameGroup = [name['name'].lower() for name in user['infor_group'] if name['name'] is not None]
        listDescriptionGroup = [name['description'].lower() for name in user['infor_group'] if
                                name['description'] is not None]
    except:
        pass
    try:
        predictionJob = user['infor']['prediction']['job'][0] if len(user['infor']['prediction']['job']) > 0 else None
    except:
        pass

    for i in range(29, 61):
        cellNameC = f'C{i}'
        cellNameJ = f'J{i}'
        cellNameM = f'M{i}'
        cellNameN = f'N{i}'
        if predictionJob == Sheet[cellNameC].value:
            dicObj['Nghề nghiệp'][Sheet[cellNameC].value] = '1'

        listKeyPosition = Sheet[cellNameJ].value.split(', ') if Sheet[cellNameJ].value is not None else []
        listKeyGroup = Sheet[cellNameM].value.split(', ') if Sheet[cellNameM].value is not None else []
        listMust = Sheet[cellNameN].value.split(', ') if Sheet[cellNameN].value is not None else []

        for key in listKeyPosition:
            for pos in listPosition:
                if pos.find(key) != -1:
                    dicObj['Nghề nghiệp'][Sheet[cellNameC].value] = '1'
        count = 0
        for key in listKeyGroup:
            if len(listMust) > 0:
                for m in listMust:
                    for group in listNameGroup:
                        if group.find(key) != -1 and group.find(m) != 1:
                            count += 1
                    for group in listDescriptionGroup:
                        if group.find(key) != -1 and group.find(m) != 1:
                            count += 1
            else:
                for group in listNameGroup:
                    if group.find(key) != -1:
                        count += 1
                for group in listDescriptionGroup:
                    if group.find(key) != -1:
                        count += 1
        dicObj['Nghề nghiệp'][Sheet[cellNameC].value] = '1' if count >= 3 else ''


def evalEdu(user, dicObj, Sheet):
    indicatorEdu = ''
    listEdu = []
    try:
        indicatorEdu = user['infor']['indicator']['educationDegree']
    except:
        pass
    try:
        listEdu = [edu['school'].lower() for edu in user['infor']['educations'] if edu['school'] is not None]
    except:
        pass

    for i in range(61, 66):
        cellNameC = f'C{i}'
        cellNameM = f'M{i}'
        if indicatorEdu == Sheet[cellNameC].value:
            dicObj['trình độ học vấn'][Sheet[cellNameC].value] = '1'

        listKeyEdu = Sheet[cellNameM].value.split(', ') if Sheet[cellNameM].value is not None else []
        for key in listKeyEdu:
            for edu in listEdu:
                if edu.find(key) != -1:
                    dicObj['trình độ học vấn'][Sheet[cellNameC].value] = '1'


def evalLanguage(user, dicObj, Sheet):
    listLanguage = []
    try:
        listLanguage = [lang.lower() for lang in user['infor']['languages'] if lang is not None]
    except:
        pass

    for i in range(66, 92):
        cellNameC = f'C{i}'
        cellNameM = f'M{i}'
        listKeyLang = Sheet[cellNameM].value.split(', ') if Sheet[cellNameM].value is not None else []
        for key in listKeyLang:
            for lang in listLanguage:
                if lang.find(key) != -1:
                    dicObj['Ngôn ngữ'][Sheet[cellNameC].value] = '1'


def evalHometown(user, dicObj, Sheet):
    listHomeTowns = []
    try:
        listHomeTowns = [town.lower() for town in user['infor']['hometowns'] if town is not None]
    except:
        pass
    listHomeTownProvinces = []
    try:
        listHomeTownProvinces = [town.lower() for town in user['infor']['hometownProvinces'] if town is not None]
    except:
        pass

    for i in range(92, 155):
        cellNameC = f'C{i}'
        cellNameM = f'M{i}'
        listKeyHometown = Sheet[cellNameM].value.split(', ') if Sheet[cellNameM].value is not None else []
        for key in listKeyHometown:
            for town in listHomeTowns:
                if town.find(key) != -1:
                    dicObj['Quê quán'][Sheet[cellNameC].value] = '1'
            for town in listHomeTownProvinces:
                if town.find(key) != -1:
                    dicObj['Quê quán'][Sheet[cellNameC].value] = '1'


def evalLocation(user, dicObj, Sheet):
    listLocation = []
    try:
        listLocation = [town.lower() for town in user['infor']['location'] if town is not None]
    except:
        pass
    listLocationProvinces = []
    try:
        listLocationProvinces = [town.lower() for town in user['infor']['locationProvinces'] if town is not None]
    except:
        pass

    for i in range(155, 218):
        cellNameC = f'C{i}'
        cellNameM = f'M{i}'
        listKeyHometown = Sheet[cellNameM].value.split(', ') if Sheet[cellNameM].value is not None else []
        for key in listKeyHometown:
            for town in listLocation:
                if town.find(key) != -1:
                    dicObj['Nơi ở hiện tại'][Sheet[cellNameC].value] = '1'
            for town in listLocationProvinces:
                if town.find(key) != -1:
                    dicObj['Nơi ở hiện tại'][Sheet[cellNameC].value] = '1'


def evalOwn(user, dicObj, Sheet):
    listNameGroup = []
    listDescriptionGroup = []
    try:
        listNameGroup = [name['name'].lower() for name in user['infor_group'] if name['name'] is not None]
        listDescriptionGroup = [name['description'].lower() for name in user['infor_group'] if
                                name['description'] is not None]
    except:
        pass

    for i in range(220, 225):
        cellNameE = f'E{i}'
        cellNameD = f'D{i}'
        cellNameC = f'C{i}'
        cellNameM = f'M{i}'
        cellNameN = f'N{i}'
        count = 0
        listKeyGroup = Sheet[cellNameM].value.split(', ') if Sheet[cellNameM].value is not None else []
        listMust = Sheet[cellNameN].value.split(', ') if Sheet[cellNameN].value is not None else []
        for key in listKeyGroup:
            if len(listMust) > 0:
                for m in listMust:
                    for group in listNameGroup:
                        if group.find(key) != -1 and group.find(m) != 1:
                            count += 1
                    for group in listDescriptionGroup:
                        if group.find(key) != -1 and group.find(m) != 1:
                            count += 1
            else:
                for group in listNameGroup:
                    if group.find(key) != -1:
                        count += 1
                for group in listDescriptionGroup:
                    if group.find(key) != -1:
                        count += 1
        dicObj['Sở hữu']['Bất động sản'][Sheet[cellNameD].value] = '1' if count >= 2 else ''

    for i in range(225, 242):
        cellNameE = f'E{i}'
        cellNameD = f'D{i}'
        cellNameC = f'C{i}'
        cellNameM = f'M{i}'
        cellNameN = f'N{i}'
        count = 0
        listKeyGroup = Sheet[cellNameM].value.split(', ') if Sheet[cellNameM].value is not None else []
        listMust = Sheet[cellNameN].value.split(', ') if Sheet[cellNameN].value is not None else []
        for key in listKeyGroup:
            if len(listMust) > 0:
                for m in listMust:
                    for group in listNameGroup:
                        if group.find(key) != -1 and group.find(m) != 1:
                            count += 1
                    for group in listDescriptionGroup:
                        if group.find(key) != -1 and group.find(m) != 1:
                            count += 1
            else:
                for group in listNameGroup:
                    if group.find(key) != -1:
                        count += 1
                for group in listDescriptionGroup:
                    if group.find(key) != -1:
                        count += 1
        dicObj['Sở hữu']['Bất động sản']['BĐS nổi bật'][Sheet[cellNameE].value] = '1' if count >= 2 else ''

    for i in range(242, 267):
        cellNameE = f'E{i}'
        cellNameD = f'D{i}'
        cellNameC = f'C{i}'
        cellNameM = f'M{i}'
        cellNameN = f'N{i}'
        count = 0
        listKeyGroup = Sheet[cellNameM].value.split(', ') if Sheet[cellNameM].value is not None else []
        listMust = Sheet[cellNameN].value.split(', ') if Sheet[cellNameN].value is not None else []
        for key in listKeyGroup:
            if len(listMust) > 0:
                for m in listMust:
                    for group in listNameGroup:
                        if group.find(key) != -1 and group.find(m) != 1:
                            count += 1
                    for group in listDescriptionGroup:
                        if group.find(key) != -1 and group.find(m) != 1:
                            count += 1
            else:
                for group in listNameGroup:
                    if group.find(key) != -1:
                        count += 1
                for group in listDescriptionGroup:
                    if group.find(key) != -1:
                        count += 1
        dicObj['Sở hữu']['Xe cộ'][Sheet[cellNameD].value] = '1' if count >= 2 else ''


def check_behavior(user , index, keywords, listMust):
    if index == "dsminer_user_core":
        count = 0
        for place in user["infor"]["checkin"]:
            name_place = place["place"]["name"].lower()
            for keyword in keywords:
                if name_place.find(keyword) != -1:
                    count = count + 1
                    break
        if count > 1:
            return 1
        else:
            return 0

    if index == "dsminer_group":
        count = 0
        for group in user["infor_group"]:
            name = group["name"].lower()
            description = group["description"].lower()
            if len(listMust) > 0:
                for m in listMust:
                    for keyword in keywords:
                        if (name.find(keyword) != -1 or description.find(keyword) != -1) and (
                                name.find(m) != -1 or description.find(m) != -1):
                            count = count + 1
                            break
            else:
                for keyword in keywords:
                    if name.find(keyword) != -1 or description.find(keyword) != -1:
                        count = count + 1
                        break
        if count > 3:
            return 1
        else:
            return 0
    if index == "dsminer_post":
        count = 0
        for post in user["infor_post"]:
            message = post["message"].lower()
            if len(listMust) > 0:
                for m in listMust:
                    for keyword in keywords:
                        if message.find(keyword) != -1 and message.find(m) != 1:
                            count = count + 1
                            break
            else:
                for keyword in keywords:
                    if message.find(keyword) != -1:
                        count = count + 1
                        break
        if count > 5:
            return 1
        else:
            return 0
    return 0

class API2:
    def get_all(userId):
        dictObj = {}
        user = API1.user(userId).get_all()
        level1 = ''
        level2 = ''
        level3 = ''
        level4 = ''
        level5 = ''
        level6 = ''
        wb = openpyxl.load_workbook('demographic_behaviorKeywords.xlsx')
        Sheet1 = wb['Sheet1']
        for i in range(3, 265):
            cellNameB = f'B{i}'
            cellNameC = f'C{i}'
            cellNameD = f'D{i}'
            cellNameE = f'E{i}'
            cellNameF = f'F{i}'
            cellNameG = f'G{i}'

            cellDataB = Sheet1[cellNameB].value
            cellDataC = Sheet1[cellNameC].value
            cellDataD = Sheet1[cellNameD].value
            cellDataE = Sheet1[cellNameE].value
            cellDataF = Sheet1[cellNameF].value
            cellDataG = Sheet1[cellNameG].value

            if cellDataB is not None:
                level1 = cellDataB
                if cellDataC is None:
                    dictObj[level1] = ''
                else:
                    dictObj[level1] = {}

            if cellDataC is not None:
                level2 = cellDataC
                if cellDataD is None:
                    dictObj[level1][level2] = ''
                else:
                    dictObj[level1][level2] = {}

            if cellDataD is not None:
                level3 = cellDataD
                if cellDataE is None:
                    dictObj[level1][level2][level3] = ''
                else:
                    dictObj[level1][level2][level3] = {}

            if cellDataE is not None:
                level4 = cellDataE
                if cellDataF is None:
                    dictObj[level1][level2][level3][level4] = ''
                else:
                    dictObj[level1][level2][level3][level4] = {}

            if cellDataF is not None:
                level5 = cellDataF
                if cellDataG is None:
                    dictObj[level1][level2][level3][level4][level5] = ''
                else:
                    dictObj[level1][level2][level3][level4][level5] = {}

            if cellDataG is not None:
                level6 = cellDataG
                dictObj[level1][level2][level3][level4][level5][level6] = ''
        evalAges(user, dictObj)
        evalRelationship(user, dictObj)
        evalGender(user, dictObj)
        evalChild(user, dictObj)
        evalJob(user, dictObj, Sheet1)
        evalEdu(user, dictObj, Sheet1)
        evalLanguage(user, dictObj, Sheet1)
        evalHometown(user, dictObj, Sheet1)
        evalLocation(user, dictObj, Sheet1)
        evalOwn(user, dictObj, Sheet1)
        for i in range(268, 1215):
            cellNameB = f'B{i}'
            cellNameC = f'C{i}'
            cellNameD = f'D{i}'
            cellNameE = f'E{i}'
            cellNameF = f'F{i}'
            cellNameG = f'G{i}'
            cellNameIndex1 = f'H{i}'
            cellNameIndex2 = f'K{i}'
            cellNameField1 = f'I{i}'
            cellNameField2 = f'L{i}'
            cellNameKeywords1 = f'J{i}'
            cellNameKeywords2 = f'M{i}'
            cellNameMust = f'N{i}'

            cellDataB = Sheet1[cellNameB].value
            cellDataC = Sheet1[cellNameC].value
            cellDataD = Sheet1[cellNameD].value
            cellDataE = Sheet1[cellNameE].value
            cellDataF = Sheet1[cellNameF].value
            cellDataG = Sheet1[cellNameG].value
            index_1 = Sheet1[cellNameIndex1].value if Sheet1[cellNameIndex1].value is not None else None
            index_2 = Sheet1[cellNameIndex2].value if Sheet1[cellNameIndex2].value is not None else None
            field_1 = Sheet1[cellNameField1].value.split(', ') if Sheet1[cellNameField1].value is not None else None
            field_2 = Sheet1[cellNameField2].value.split(', ') if Sheet1[cellNameField2].value is not None else None
            keywords_1 = Sheet1[cellNameKeywords1].value.split(', ') if Sheet1[cellNameKeywords1].value is not None else None
            keywords_2 = Sheet1[cellNameKeywords2].value.split(', ') if Sheet1[cellNameKeywords2].value is not None else None
            must = Sheet1[cellNameMust].value.split(', ') if Sheet1[cellNameMust].value is not None else []

            value = 0
            if index_1 != None and keywords_1 != None and index_2 == None and keywords_2 == None:
                value = check_behavior(user,index_1, keywords_1, must)
            if index_1 == None and keywords_1 == None and index_2 != None and keywords_2 != None:
                value = check_behavior(user , index_2, keywords_2, must)
            if index_1 != None and keywords_1 != None and index_2 != None and keywords_2 != None:
                value = check_behavior(user ,index_2, keywords_2, must) or check_behavior(user ,index_1, keywords_1, must)
            if value == 0:
                value = ""
            if cellDataB is not None:
                level1 = cellDataB
                if cellDataC is None:
                    dictObj[level1] = value
                else:
                    dictObj[level1] = {}

            if cellDataC is not None:
                level2 = cellDataC
                if cellDataD is None:
                    dictObj[level1][level2] = value
                else:
                    dictObj[level1][level2] = {}

            if cellDataD is not None:
                level3 = cellDataD
                if cellDataE is None:
                    dictObj[level1][level2][level3] = value
                else:
                    dictObj[level1][level2][level3] = {}

            if cellDataE is not None:
                level4 = cellDataE
                if cellDataF is None:
                    dictObj[level1][level2][level3][level4] = value
                else:
                    dictObj[level1][level2][level3][level4] = {}

            if cellDataF is not None:
                level5 = cellDataF
                if cellDataG is None:
                    dictObj[level1][level2][level3][level4][level5] = value
                else:
                    dictObj[level1][level2][level3][level4][level5] = {}

            if cellDataG is not None:
                level6 = cellDataG
                dictObj[level1][level2][level3][level4][level5][level6] = value

        wb.close()
        return dictObj