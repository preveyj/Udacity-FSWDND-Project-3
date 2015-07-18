def answer(n):
    """
    Given some base 10 integer n, return the smallest new base in which
    n becomes a palindrome.
    
    https://stackoverflow.com/questions/2267362/convert-integer-to-a-string-in-a-given-numeric-base-in-python
        int(str,base) gets int of base from string
        str(int(str, base))
        
    https://docs.python.org/2/library/functions.html#int
        int(str, base) works if base is given; base must be 2-36
        if higher base numbers are needed, things might need to get silly
    """
    nAsString = str(n)
    
    for base in range(2, 36):
        testMe = str(int(nAsString, base=base))
        testMeLen = len(testMe)
        
        isPalindrome = True
        
        for i in range(0, (testMeLen/2)):
            if testMe[i] != testMe[testMeLen - 1 - i]:
                isPalindrome = False
                break
        
        if isPalindrome == True:
            return base
    
    return 0

for x in range(3, 1000):
	print answer(x)