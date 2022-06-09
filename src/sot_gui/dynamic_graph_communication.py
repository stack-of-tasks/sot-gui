from typing import Any, List
from sot_ipython_connection.sot_client import SOTClient


class DynamicGraphCommunication():
    """ This class allows to communicate with a SoT dynamic graph on a remote kernel. """

    def __init__(self):
        self._client: SOTClient = None
        self.connect_to_kernel()
        

    def _import_dynamic_graph(self) -> None:
        """ Imports the dynamic graph.
            Raises a ConnectionError if the kernel is not running.
        """
        self.run("import dynamic_graph as dg", False)


    def connect_to_kernel(self):
        """ Recreates a client that will connect to the latest kernel. """

        # It's not possible to keep the client and reconnect it to a new kernel:
        # we have to create a new one
        self._client = SOTClient()
        try:
            self._import_dynamic_graph()
        except ConnectionError:
            print('DynamicGraphCommunication.__init__: could not import dynamic graph' +
                ' into kernel (no connection)')


    def run(self, code: str, ret_value: bool = True) -> Any:
        """ Runs code on the remote server, and returns a value if needed. """
        response = self._client.run_python_command(code)
            
        if response.stdout:
            print(response.stdout)
        if response.stderr:
            print(response.stderr)
        
        if response.result:
            if not ret_value:
                return
            return response.result


    def get_all_entities_names(self) -> List[str]:
        """ Returns a list of the names of the dynamic graph's entities. """
        return self.run("dg.entity.Entity.entities.keys()")


    def entity_exists(self, entity_name: str) -> bool:
        """ Returns True if the dynamic graph contains an entity named
            `entity_name`.
        """
        return self.run(f"{entity_name} + in dg.node.Entity.entities")


    def get_entity_type(self, entity_name: str) -> str:
        """ Returns the type of the entity, as a string. """
        return self.run(f"dg.entity.Entity.entities['{entity_name}'].className")


    def get_entity_signals(self, entity_name: str) -> List[str]:
        """ Returns a list of the entity's signals information
            (e.g `'Add_of_double(add1)::input(double)::sin0'`).
        """
        return self.run(f"[ s.name for s in dg.entity.Entity\
            .entities['{entity_name}'].signals() ]")


    def is_signal_plugged(self, entity_name: str, signal_name: str) -> bool:
        """ Returns True if the signal is plugged to another entity. """
        return self.run(f"dg.entity.Entity.entities\
            ['{entity_name}'].signal('{signal_name}').isPlugged()")


    def get_linked_plug(self, entity_name: str, plug_name: str) -> str:
        """ Returns the name of the plug linked to an entity's given plug. """
        return self.run(f"dg.entity.Entity.entities\
            ['{entity_name}'].signal('{plug_name}').getPlugged().name")


    def get_signal_value(self, entity_name: str, plug_name: str) -> Any:
        """ Returns the value of an entity's given plug. """
        return self.run(f"dg.entity.Entity.entities\
            ['{entity_name}'].signal('{plug_name}').value")
