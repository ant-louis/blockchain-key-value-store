from requests import get, post, exceptions
from time import sleep
from threading import Thread

class Broadcast():

    def __init__(self, peers, ip):
        self._peers = peers
        self._heartbeat = True
        print("Before starting thread")
        heart_beat = Thread(target=self.heart_beat)
        heart_beat.start()
        self._correct = peers
        self._ip = ip

    def add_peer(self, peer):
        if peer not in self._peers:
            self._peers.append(peer)

    def get_peers(self):
        return self._correct


    def send(self, message_type, message):
        """
        Lazy Reliable Broadcast
        """
        self.beb_send(message_type, message, self._ip)



    def beb_deliver(self, message_type, message, sender):
        """
        When 
        """
        if message not in self._from[sender]:
            result = (message_type, message)
            self._from[sender].append(message)
            if sender not in self._correct:
                self.beb_send(message_type, message, sender)
            return result


    def beb_send(self, message_type, message, sender):
        """ 
        Best effort broadcast
        """
        results = {}
        for peer in self._peers:
            url = "http://{}/message".format(peer)
            response = self.send_to_one(peer, message_type, message, sender)
            if response == "Exception" or response.status_code != 200:
                results[peer] = "Exception"
            else:
                results[peer] = response.json()
        return results


    
    def send_to_one(self, peer, message_type, message, sender, timeout = 1):
        if peer not in self._correct:
            return "Uncorrect process"
        url = "http://{}/message".format(peer)
        try:
            response = get(url, params={"type": message_type, "message": message, "sender": sender}, timeout=1)
        except exceptions.RequestException:
            return "Exception"
        return response
        

    def heart_beat(self):
        uncorrect_process = {}
        while self._heartbeat:
            for peer in self._peers:
                response = self.send_to_one(peer, message_type="heartbeat", message="h")
                if peer in self._correct and (response == "Exception" or response.status_code != 200):
                    self._correct.remove(peer)
                    uncorrect_process[peer] = 1
                elif peer not in self._correct and response.json()["Result"] == "Ok":
                    self._correct(peer)
                elif peer not in self._correct:
                    uncorrect_process[peer] += 1
                    if uncorrect_process[peer] > 20:
                        self._peers.remove(peer)
                        
            sleep(30)

