def readdata():
    Users = {}
    with open('USERS.txt') as data:
        while True:
            line = data.readline()
            if not line:
                break

            line = line[:-1]
            name, id = line.split(':')
            userInfo = {}
            for i in range(0,5):
                line = data.readline()[:-1]
                first, second = line.split(':')
                userInfo[first] = second
            Users[id] = userInfo
            line = data.readline()
    return Users
