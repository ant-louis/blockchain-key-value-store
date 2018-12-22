from requests import get, post, exceptions
from time import sleep
from threading import Thread

class Broadcast():

    def __init__(self, peers, ip):
        self._peers = peers
        self._correct = peers
        self._ip = ip

        #Intialize the from dictionary for peers
        self._from = {}
        for peer in self._peers:
            self._from[peer] = []

        self._from[self._ip] = []
        # Start heartbeat
        self._heartbeat = True
        heart_beat = Thread(target=self.heart_beat)
        heart_beat.start()

    def add_peer(self, peer):
        """
        Add the peer to the list of peers 
        if it is not already in
        """
        if peer not in self._peers and peer != self._ip:
            self._correct.add(peer)
            self._peers.add(peer)
            self._from[peer] = []

    def get_peers(self):
        """
        Return the list of peers
        """
        return self._correct

    def broadcast(self, message_type, message):
        """
        Lazy Reliable Broadcast

        Arguments:
        ----------
        - `message_type`: type of message to send {transaction, block}
        - `message`: message to send
        """
        self._from[self._ip].append(message)
        self.beb_send(message_type, message, self._ip)

    def deliver(self, message_type, message, sender):
        """
        Deliver the message. If the sender is not
        a correct processe anymore the message is re-broadcast     

        Arguments:
        ----------
        - `message_type`: type of message to send {transaction, block}
        - `message`: message to send
        - `sender`: adress of the sender

        Returns:
        ----------
        - `deliver`: a tuple with :
                        - a boolean if the message is new (True)
                            or if it has arleady been recieved
                        - a list containg the message_type, the message
                            and the sender if the boolean is True.
                            An empty list otherwise
        """
        if message not in self._from[sender]:
            result = [message_type, message, sender]
            self._from[sender].append(message)
            if sender not in self._correct:
                # The sender is not a correct process anymore
                self.beb_send(message_type, message, sender)
            return (True, result)
        else:
            return (False,[])

    def beb_send(self, message_type, message, sender):
        """
        Best effort broadcast.
        Send the message to every peer

        Arguments:
        ----------
        - `type`: type of message to send {transaction, block}
        - `message`: message to send
        - `sender`: adress of the sender
        """
        for peer in self._peers:
            print("Sending {} to peer {}".format(message_type, peer))
            params = {"type": message_type, "message": message, "sender": sender}
            try:
                send_to_one(peer, "broadcast", params)
            except exceptions.RequestException:
                pass

    def heart_beat(self):
        """
        Perfect failure detector.

        Send heartbeat to every peer and wait resopnse.

        If the response comes and its satuts_code is 200
        the process is alive

        If the process was alive the an error is raised the process 
        is mark as not correct anymore and the counter begins

        If the process was uncorrect and a error is raised, 
        the counter is incremented. If it reached 10 
        (the process does not respond to 10 consecutive heartbeat)
        it is removed from the list of peers.

        If the process was marked as uncorrect and the heartbeat
        response does not raise error. The process is marked as correct
        """
        uncorrect_process = {}
        to_remove_correct = []
        to_remove_peer = []
        while self._heartbeat:
            for peer in self._peers:
                to_remove_correct = []
                to_remove_peer = []
                try:
                    send_to_one(peer, path="heartbeat")
                except exceptions.RequestException:
                    if peer in self._correct:
                        to_remove_correct.append(peer)
                        uncorrect_process[peer] = 1
                        continue
                        
                    else:
                        uncorrect_process[peer] += 1
                        if uncorrect_process[peer] > 10:
                            to_remove_peer.append(peer)
                            del self._from[peer]
                        continue

                if peer not in self._correct:
                    self._correct.add(peer)
            for peer in to_remove_correct:
                self._correct.remove(peer)
            for peer in to_remove_peer:
                self._peers.remove(peer)
            sleep(10)


def send_to_one(peer, path, message = ""):
    """
    Send a message to a particular node

    Arguments:
    ----------
    - `peer`: the node to send the message
    - `path`: message to send
    - `sender`: adress of the sender
    """
    url = "http://{}/{}".format(peer, path)
    response = get(url, params=message, timeout = 10)
    if response.status_code != 200:
        raise exceptions.RequestException('Bad return error')
    return response