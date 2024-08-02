import os
import sys

TokenKey = sys.argv[1]

os.mkdir("{}".format(TokenKey))
os.makedirs("{}/dataset".format(TokenKey))
os.makedirs("{}/har".format(TokenKey))
os.makedirs("{}/hef".format(TokenKey))
os.makedirs("{}/svg".format(TokenKey))