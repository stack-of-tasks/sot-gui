from typing import Any, List
from sot_ipython_connection.sot_client import SOTClient


class DynamicGraphCommunication():
    """ This class allows to communicate with a SoT dynamic graph, which can
        be local or on a remote server.
    """
    _isLocal = False


    @staticmethod
    def dgIsLocal() -> None:
      DynamicGraphCommunication._isLocal = True


    def __init__(self) -> None:
        self._client = SOTClient()
        self._localVars  = {}
        self._globalVars = {}
        self._importDynamicGraph()


    def run(self, code: str, retValue: bool = True) -> Any:
        """ Runs code, either locally or on the remote server. """
        # TODO: should the code be encoded?
        if DynamicGraphCommunication._isLocal:
          return self.runLocalCode(code, retValue)
        else:
          return self.runRemoteCode(code, retValue)


    def runLocalCode(self, code: str, retValue: bool) -> Any | None:
        """ Runs code locally, and returns a value if needed. """
        localVars = None
        globalVars = self._globalVars
        if retValue:
          exec(f"_returnValue = {code}", globalVars, localVars)
          return eval("_returnValue", globalVars, localVars)
        else:
          exec(code, globalVars, localVars)


    def runRemoteCode(self, code: str, retValue: bool) -> Any | None:
        """ Runs code on the remote server, and returns a value if needed. """
        try:
            # TODO: reconnect if the server was restarted
            # -> SOTClient.is_kernel_alive() (-> bool)

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


    def _importDynamicGraph(self) -> None:
        """ Imports the dynamic graph. """
        self.run("import dynamic_graph as dg", False)


    def getAllEntitiesNames(self) -> List[str]:
        """ Returns a list of the names of the dynamic graph's entities. """
        return self.run("dg.entity.Entity.entities.keys()")


    def entityExists(self, entityName: str) -> bool:
        """ Returns True if the dynamic graph contains an entity named
            `entityName`.
        """
        return self.run(f"{entityName} + in dg.node.Entity.entities")


    def getEntityType(self, entityName: str) -> str:
        """ Returns the type of the entity, as a string. """
        return self.run(f"dg.entity.Entity.entities['{entityName}'].className")


    def getEntitySignals(self, entityName: str) -> List[str]:
        """ Returns a list of the entity's signals information
            (e.g `'Add_of_double(add1)::input(double)::sin0'`).
        """
        return self.run(f"[ s.name for s in dg.entity.Entity\
            .entities['{entityName}'].signals() ]")


    def isSignalPlugged(self, entityName: str, signalName: str) -> bool:
        """ Returns True if the signal is plugged to another entity. """
        return self.run(f"dg.entity.Entity.entities\
            ['{entityName}'].signal('{signalName}').isPlugged()")


    def getLinkedPlugName(self, entityName: str, plugName: str) -> str:
        """ Returns the name of the plug linked to an entity's given plug. """
        return self.run(f"dg.entity.Entity.entities\
            ['{entityName}'].signal('{plugName}').getPlugged().name")


    def getSignalValue(self, entityName: str, plugName: str) -> Any:
        """ Returns the value of an entity's given plug. """
        return self.run(f"dg.entity.Entity.entities\
            ['{entityName}'].signal('{plugName}').value")
