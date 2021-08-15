from test.Test import testConstructFirstSet, testConstructFollowSet, testConstructLR1
from algorithm.FA import RegExpToDFA

if __name__ == '__main__':
    # testConstructFirstSet()
    # testConstructFollowSet()
    # testConstructLR1()
    RegExpToDFA('abcd[(kmn)*,(xyz)+]?abc')