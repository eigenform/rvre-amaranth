""" Constants used to parameterize the design. 
"""

class RVREParams():
    def __init__(self, prf_size=64):
        self.prf_size = prf_size

PARAM = RVREParams(
    prf_size=64,
)
