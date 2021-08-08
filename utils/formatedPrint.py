

def printSet(First):
    """printSet 打印First集或者Follow集

    Args:
        First ([type]): [description]
    """    
    for vn in First:
        print('VN %s' % str(vn))
        for vt in First[vn]:
            print('VT %s' % str(vt))
        print('VN %s end' % str(vn))