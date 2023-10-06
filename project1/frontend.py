import xmlrpc.client
import xmlrpc.server
from socketserver import ThreadingMixIn
from xmlrpc.server import SimpleXMLRPCServer
import multiprocessing
import time
import random

kvsServers = dict()
baseAddr = "http://localhost:"
baseServerPort = 9000

class SimpleThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
        pass

class FrontendRPCServer:
    # TODO: You need to implement details for these functions.
    def __init__(self):
        # Implement a lock for every server
        self.locks = {}
        # Parameters
        self.timeout = 1.5

    def parallel_worker(self, func, params, queue):
        if 'key' in params and 'value' in params:
            # Put request
            result = func(params['key'], params['value'])
            if result[0] == "Put OK":
                # Release the lock
                # If the server with number serverId suddenly disappeared, accessing the dict will raise error, so check that
                if params['serverId'] in self.locks:
                    self.locks[params['serverId']] = False
        elif 'key' in params:
            # Check if lock is engaged and wait for the lock to be free (this process will be killed at timeout)
            currServerId = params['serverId']
            while self.locks[currServerId]: # To be killed by main calling function
                pass
            # Get request
            result = func(params['key'])
        queue.put((params, f"{result}---{str(self.locks)}---{params['serverId']}---{params['serverId'] in self.locks}----{result[0]}---"))

    ## put: This function routes requests from clients to proper
    ## servers that are responsible for inserting a new key-value
    ## pair or updating an existing one.
    def put(self, key, value):
        # Lock all servers
        for serverId in kvsServers:
            self.locks[serverId] = True

        # Start a parallel process to put to all servers
        manager = multiprocessing.Manager()
        queue = manager.Queue()

        # Prepare a list of jobs to parallelize
        calls = [(kvsServers[serverId].put, {'serverId': serverId, 'key': key, 'value': value}) for serverId in kvsServers]
        processes = []
        for func, params in calls:
            process = multiprocessing.Process(target=self.parallel_worker, args=(func, params, queue))
            processes.append(process)
            process.start()
        
        # Now collect responses
        for i, process in enumerate(processes):
            process.join(timeout=self.timeout)
            # Kill the job if taking too long
            if process.is_alive():
                process.terminate()
                queue.put((calls[i][1], "Error: Timeout"))
            process.join()

        # Process the success and failure cases
        result_str = ""
        while not queue.empty():
            params, result = queue.get()
            result_str += f"Call with params {params} returned: {result}"

        # See which servers are still locked and assume them to be dead and remove that
        result_str += f"{str(self.locks)}"
        for serverId in self.locks:
            if self.locks[serverId]:
                # TODO: pop, only print for now
                self.shutdownServer(serverId)
                result_str += f". Failed node: {serverId}"

        return result_str

    ## get: This function routes requests from clients to proper
    ## servers that are responsible for getting the value
    ## associated with the given key.
    def get(self, key):
        # Randomly sample a serverId from kvsServers and use that to get the value, pause for the lock in worker function
        while len(kvsServers) > 0:
            chosenServerId = random.choice(list(kvsServers.keys()))

            manager = multiprocessing.Manager()
            queue = manager.Queue()
            # Singleton list for get
            calls = [(kvsServers[chosenServerId].get, {'serverId': chosenServerId, 'key': key})]
            processes = []
            for func, params in calls:
                process = multiprocessing.Process(target=self.parallel_worker, args=(func, params, queue))
                processes.append(process)
                process.start()
            
            # Now collect response
            for i, process in enumerate(processes):
                process.join(timeout=self.timeout)
                # Kill the job if read is taking too long
                if process.is_alive():
                    process.terminate()
                    queue.put((calls[i][1], "Error: Get Timeout"))
                process.join()
            
            # Process the success and failure cases
            while not queue.empty():
                params, result = queue.get()
                if result[0] == "Get OK":
                    # result[1] has the value
                    value = result[1]
                else:
                    value = None

            # If success, break
            if value:
                return f"Value is : {value}"
            # Remove the server here
            else:
                # chosenServerId needs to be killed
                self.shutdownServer(chosenServerId)

        serverId = key % len(kvsServers)
        return kvsServers[serverId].get(key)

    ## printKVPairs: This function routes requests to servers
    ## matched with the given serverIds.
    def printKVPairs(self, serverId):
        return kvsServers[serverId].printKVPairs()

    ## addServer: This function registers a new server with the
    ## serverId to the cluster membership.
    def addServer(self, serverId):
        kvsServers[serverId] = xmlrpc.client.ServerProxy(baseAddr + str(baseServerPort + serverId))
        return "Success"

    ## listServer: This function prints out a list of servers that
    ## are currently active/alive inside the cluster.
    def listServer(self):
        serverList = []
        for serverId, rpcHandle in kvsServers.items():
            serverList.append(serverId)
        return serverList

    ## shutdownServer: This function routes the shutdown request to
    ## a server matched with the specified serverId to let the corresponding
    ## server terminate normally.
    def shutdownServer(self, serverId):
        result = kvsServers[serverId].shutdownServer()
        kvsServers.pop(serverId)
        return result

server = SimpleThreadedXMLRPCServer(("localhost", 8001))
server.register_instance(FrontendRPCServer())

server.serve_forever()
