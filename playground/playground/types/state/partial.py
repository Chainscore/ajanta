from playground.types.state.delta import Delta
from playground.types.state.iota import Iota
from playground.types.state.phi import Phi
from playground.types.state.chi import Chi
from tsrkit_types import structure


@structure
class GhostPartial:
    # d
    service_accounts: Delta
    # i
    validator_keys: Iota
    # q
    authorizer_keys: Phi
    # m, a, v, z
    privileges: Chi
    
    def clone(self):
        return self