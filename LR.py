from collections import defaultdict
from enum import Enum
import re
from test.Test import testConstructFirstSet, testConstructFollowSet, testConstructLR1

if __name__ == '__main__':
    testConstructFirstSet()
    testConstructFollowSet()
    testConstructLR1()
