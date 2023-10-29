import pyteal as pt
from beaker.lib.storage import BoxMapping


class MappingState:
    deposits = BoxMapping(pt.abi.Uint64, pt.abi.Address)
