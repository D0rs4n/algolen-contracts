import pyteal as pt
from beaker.lib.storage import BoxMapping


class AlgolenListing(pt.abi.NamedTuple):
    asset_id: pt.abi.Field[pt.abi.Uint64]
    estimated_price_in_microalgos: pt.abi.Field[pt.abi.Uint64]
    owner: pt.abi.Field[pt.abi.Address]
    is_available_for_rent: pt.abi.Field[pt.abi.Bool]


class AlgolenRent(pt.abi.NamedTuple):
    next_rent_due_timestamp: pt.abi.Field[pt.abi.Uint64]
    asset_owner: pt.abi.Field[pt.abi.Address]
    asset_renter: pt.abi.Field[pt.abi.Address]


class MappingState:
    listings = BoxMapping(pt.abi.Uint64, AlgolenListing, prefix=pt.Bytes("p"))
    deposits = BoxMapping(pt.abi.Uint64, pt.abi.Address, prefix=pt.Bytes("d"))
    rents = BoxMapping(pt.abi.Uint64, AlgolenRent, prefix=pt.Bytes("r"))
