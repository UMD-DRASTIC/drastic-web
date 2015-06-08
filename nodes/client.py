"""
The NodeClient class is responsible for connecting to
indigo agents and interacting with them to:

    1. Determine their internal state
    2. Determine their connectivity status
"""
import requests

class NodeClient(object):

    def __init__(self, address):
        self.address = address

    def get_state(self):
        """
        Used to both obtain current state and also
        to check connectivity status.

        Returns a boolean and a dictionary, the boolean
        denotes whether the node was reachable, and the
        dictionary will contain metrics made available by the node.
        """
        data = {}
        try:
            data = requests.get('http://{}/api/status'.format(self.address), timeout=0.2)
        except:
            return False, {}

        return True, data