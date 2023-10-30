import pyteal as pt
from beaker.lib.storage import BoxMapping


class FracticNFTPool(pt.abi.NamedTuple):
    time_limit_elapsed: pt.abi.Field[pt.abi.Uint64]
    creator: pt.abi.Field[pt.abi.Address]
    max_fraction: pt.abi.Field[pt.abi.Uint64]
    asset_id: pt.abi.Field[pt.abi.Uint64]


class MappingState:
    deposits = BoxMapping(pt.abi.Uint64, pt.abi.Address)
    pools = BoxMapping(pt.abi.Uint64, FracticNFTPool)