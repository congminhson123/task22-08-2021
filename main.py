from API2 import API2

if __name__ == "__main__":
    user_id = "100003717317472"
    # return dictionary (1k field)
    dictObj = API2.get_all(user_id)
    print(dictObj)