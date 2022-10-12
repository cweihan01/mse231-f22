"""
Test file to test piping tweets from zipped file to stdin.
"""

import sys

i = 0
for line in sys.stdin:
    i += 1
print(i)
