# Problem: given strings A and B, determine the if A has any anagrams of B, how many, and where they start.

# My Comments:  I had to look up what an anogram is, basically it's any arrangement of letters from B that can be in A - for example
# 'cat' and 'act' are anagrams but so is 'cta'.  I still don't understand if there can be repeated letters in an anagram (I thinks so).
# 'beer' and 'rebe' are anagrams? Probably



def stringify(count, startIndexes):
    s = "" + str(count)
    for i in startIndexes:
        s = s + " " + str(i)
    return s

def anagram(a, b):
    lenA = len(a)
    lenB = len(b)

    if lenB > lenA:
        return ""

    letters = {}
    for c in b:
        if c in letters:
            letters[c] = letters[c] + 1
        else:
            letters[c] = 1

    count = 0
    startIndexes = []
    for i in range(lenA):
        if i + lenB > lenA:
            return stringify(count, startIndexes)

        checkWord = a[i:i+lenB]
        lettersCount = {}
        for c in checkWord:
            if c not in letters:
                break

            if c not in lettersCount:
                lettersCount[c] = 1
            else:
                lettersCount[c] = lettersCount[c] + 1

        if lettersCount == letters:
            count = count + 1
            startIndexes.append(i)

    return stringify(count, startIndexes)

import unittest
class Tests(unittest.TestCase):
    def setUp(self):
        self.exampleInput = ['abdcghbaabcdij bcda', 'bbbababaaabbbb ab']

    def test_firstExample(self):
        a, b = self.exampleInput[0].split(' ')
        self.assertEqual('2 0 8', anagram(a, b))

    def test_secondExample(self):
        a, b = self.exampleInput[1].split(' ')
        self.assertEqual('6 2 3 4 5 6 9', anagram(a, b))