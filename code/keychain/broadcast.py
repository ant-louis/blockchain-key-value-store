from requests import get, post, exceptions


class Peer:
    def __init__(self, address):
        """Address of the peer.

        Can be extended if desired.
        """
        self._address = address
    def get_address(self):
        return self._address


class Broadcast():

    def __init__(self, peers):
        self._peers = peers

    def send(self, message_type, message):
        """ 
        Best effort broadcast
        """
        results = {}
        for peer in self._peers:
            url = "http://{}/message".format(peer.get_address())
            try:
                response = get(url, params={"type": message_type, "message": message}, timeout=1)
            except exceptions.Timeout:
                print("Time out exception")
                continue
            if response.status_code != 200:
                print("Unable to reach a node")
                return
            results[peer.get_address()] = response.json()
        return results


    def add_peer(self, peer):
        new_peer = Peer(peer)
        if new_peer.get_address() not in [peer.get_address() for peer in self._peers]:
            self._peers.append(new_peer)

    def get_peers(self):
        return self._peers