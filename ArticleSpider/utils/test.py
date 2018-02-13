# 二分查找 递归每次找到中间值然后左大小区分

def binary_search(alist, item):
    if len(alist) == 0:
        return False
    else:
        mid = len(alist) // 2
        if alist[mid] == item:
            return True
        if alist[mid] > item:
            return binary_search(alist[:mid], item)
        else:
            return binary_search(alist[mid + 1:], item)


a = [2, 51, 23, 5, 546, 24, 345, 32]

print(binary_search(a, 546))

# 选择排序
