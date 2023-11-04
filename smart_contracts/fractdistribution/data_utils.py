import pyteal as pt
from beaker.lib.storage import BoxMapping
from beaker import GlobalStateValue


class FracticNFTPool(pt.abi.NamedTuple):
    expiry: pt.abi.Field[pt.abi.Uint64]
    creator: pt.abi.Field[pt.abi.Address]
    max_fraction: pt.abi.Field[pt.abi.Uint64]
    asset_id: pt.abi.Field[pt.abi.Uint64]
    price_per_fraction_in_micro_algos: pt.abi.Field[pt.abi.Uint64]


class MappingState:
    pools = BoxMapping(pt.abi.String, FracticNFTPool, prefix=pt.Bytes("p"))
    deposits = BoxMapping(pt.abi.Uint64, pt.abi.Address, prefix=pt.Bytes("d"))
    dao = GlobalStateValue(pt.TealType.bytes, default=pt.Global.zero_address())
