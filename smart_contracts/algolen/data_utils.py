import pyteal as pt
from beaker.lib.storage import BoxMapping


class AlgolenListing(pt.abi.NamedTuple):
    deposit: pt.abi.Field[pt.abi.Uint64]
    price_per_day: pt.abi.Field[pt.abi.Uint64]
    max_duration_in_days: pt.abi.Field[pt.abi.Uint64]
    owner: pt.abi.Field[pt.abi.Address]


class AlgolenRent(pt.abi.NamedTuple):
    end_date: pt.abi.Field[pt.abi.Uint64]
    deposit: pt.abi.Field[pt.abi.Uint64]
    asset_owner: pt.abi.Field[pt.abi.Address]
    asset_renter: pt.abi.Field[pt.abi.Address]


class MappingState:
    listings = BoxMapping(pt.abi.Uint64, AlgolenListing)
    rents = BoxMapping(pt.abi.Uint64, AlgolenRent)
