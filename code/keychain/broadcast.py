from requests import get, post, exceptions
from time import sleep
from threading import Thread

class Broadcast():

    def __init__(self, peers, ip):
        self._peers = peers
        self._correct = peers
        self._ip = ip

        self._from = {}
        for peer in self._peers:
            self._from[peer] = []

        # Start heartbeat
        self._heartbeat = True
        print("Before starting thread")
        heart_beat = Thread(target=self.heart_beat)
        heart_beat.start()

    def add_peer(self, peer):
        if peer not in self._peers:
            self._peers.append(peer)
            self._from[peer] = []

    def get_peers(self):
        return self._correct

    def broadcast(self, message_type, message):
        """
        Lazy Reliable Broadcast
        """
        self.beb_send(message_type, message, self._ip)

    def beb_deliver(self, message_type, message, sender):
        if message not in self._from[sender]:
            result = [message_type, message, sender]
            self._from[sender].append(message)
            if sender not in self._correct:
                self.beb_send(message_type, message, sender)
            return (True, result)
        else:
            return (False,[])

    def beb_send(self, message_type, message, sender):
        """ 
        Best effort broadcast
        """
        for peer in self._peers:
            params = {"message_type": message_type, "message": message, "sender": sender}
            try:
                send_to_one(peer, "broadcast", params)
            except exceptions.RequestException:
                pass

    

    def heart_beat(self):
        uncorrect_process = {}
        while self._heartbeat:
            for peer in self._peers:
                try:
                    send_to_one(peer, path="heartbeat")
                except exceptions.RequestException:
                    if peer in self._correct:
                        self._correct.remove(peer)
                        uncorrect_process[peer] = 1
                    else:
                        uncorrect_process[peer] += 1
                        if uncorrect_process[peer] > 10:
                            self._peers.remove(peer)
                            del self._from[peer]
                if peer not in self._correct:
                    self._correct.append(peer)
            sleep(10)


def send_to_one(peer, path, message = ""):
    url = "http://{}/{}".format(peer, path)
    response = get(url, params=message, timeout = 1)
    if response.status_code != 200:
        raise exceptions.RequestException('Bad return error')
    return response