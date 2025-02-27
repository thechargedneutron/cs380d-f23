import argparse
import xmlrpc.client
import xmlrpc.server

serverId = 0
basePort = 9000

class KVSRPCServer:
    # TODO: You need to implement details for these functions.
    def __init__(self):
        self.storage = {}

    ## put: Insert a new-key-value pair or updates an existing
    ## one with new one if the same key already exists.
    def put(self, key, value):
        self.storage[key] = value
        return "[Server " + str(serverId) + "] Done. Receive a put request: " + "Key = " + str(key) + ", Val = " + str(value)

    ## get: Get the value associated with the given key.
    def get(self, key):
        return 'Value is : {}'.format(self.storage[key])
        return "[Server " + str(serverId) + "] Receive a get request: " + "Key = " + str(key)

    ## printKVPairs: Print all the key-value pairs at this server.
    def printKVPairs(self):
        for key in self.storage:
            print(key, self.storage[key])
        return "[Server " + str(serverId) + "] Receive a request printing all KV pairs stored in this server"

    ## shutdownServer: Terminate the server itself normally.
    def shutdownServer(self):
        return "[Server " + str(serverId) + "] Receive a request for a normal shutdown"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '''To be added.''')

    parser.add_argument('-i', '--id', nargs=1, type=int, metavar='I',
                        help='Server id (required)', dest='serverId', required=True)

    args = parser.parse_args()

    serverId = args.serverId[0]

    server = xmlrpc.server.SimpleXMLRPCServer(("localhost", basePort + serverId))
    server.register_instance(KVSRPCServer())

    server.serve_forever()
