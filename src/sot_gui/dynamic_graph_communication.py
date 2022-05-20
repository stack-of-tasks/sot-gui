from sot_ipython_connection.sot_client import SOTClient


class DynamicGraphCommunication():
    _isLocal = False

    def __init__(self):
        self._client = SOTClient()
        self._localVars  = {}
        self._globalVars = {}
        self._init()


    def _init(self):
        self.run("import dynamic_graph as dg", False)


    @staticmethod
    def dgIsLocal():
      DynamicGraphCommunication._isLocal = True


    def run(self, code, retValue = True):
        if DynamicGraphCommunication._isLocal:
          return self.runLocalCode(code, retValue)
        else:
          return self.runRemoteCode(code, retValue, True)


    def runLocalCode(self, code, retValue):
        localVars = None
        globalVars = self._globalVars
        if retValue:
          exec(f"_returnValue = {code}", globalVars, localVars)
          return eval("_returnValue", globalVars, localVars)
        else:
          exec(code, globalVars, localVars)


    def runRemoteCode(self, code, retValue, retry = True):
        try:
            # TODO: reconnect if the server was restarted
            # -> SOTClient.is_kernel_alive() (-> Boolean)

            response = self._client.run_python_command(code)
                
            if response.stdout:
                print(response.stdout)
            if response.stderr:
                print(response.stderr)
            
            if response.result:
                if not retValue:
                    return
                return response.result

        except: # TODO: try to reconnect?
            ...
