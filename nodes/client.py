"""
The NodeClient class is responsible for connecting to
indigo agents and interacting with them to:

    1. Determine their internal state
    2. Determine their connectivity status
"""
import requests

import logging
logger = logging.getLogger("indigo")

def choose_client():
    """
    Choose a client and return a NodeClient instance
    """
    # TODO: Only return active nodes
    # TODO: Do not only return localhost
    return NodeClient("127.0.0.1:9000")


class NodeClient(object):

    def __init__(self, address):
        self.address = address

    def notify(self, resource_id, event):
        """
        Passes the event and resource_id to the node so that it
        can act on the event itself.
        """
        data = {
            "resource": resource_id,
            "event": event
        }

        try:
            r = requests.post('http://{}/notify'.format(self.address), data=data, timeout=0.2)
        except Exception, e:
            logger.exception(e)
            return False

        return r.status_code == requests.codes.ok

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
            data = requests.get('http://{}/metrics'.format(self.address), timeout=0.2)
        except Exception, e:
            logger.exception(e)
            return False, {}

        return True, data.json()