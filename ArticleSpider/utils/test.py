def longestIncreaseSubarray(inputList):
    temp = inputList[0]
    temp_list = []
    temp_list.append(temp)
    for x in inputList[1:]:
        if x > temp:
            temp_list.append(x)
            temp = x
        else:
            break
    print(temp_list)


l =  [1, 5, 4, 7, 9]
longestIncreaseSubarray(l)
