import pyteal as pt
from beaker.lib.storage import BoxMapping


class AlgolenListing(pt.abi.NamedTuple):
    asset_id: pt.abi.Field[pt.abi.Uint64]
    estimated_price_in_microalgos: pt.abi.Field[pt.abi.Uint64]


class MappingState:
    listings = BoxMapping(pt.abi.Uint64, AlgolenListing, prefix=pt.Bytes("p"))
    deposits = BoxMapping(pt.abi.Uint64, pt.abi.Address, prefix=pt.Bytes("d"))
