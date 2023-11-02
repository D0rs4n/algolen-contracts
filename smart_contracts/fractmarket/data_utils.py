import pyteal as pt
from beaker.lib.storage import BoxMapping


class FracticBuyOrder(pt.abi.NamedTuple):
    creator: pt.abi.Field[pt.abi.Address]
    asset_id: pt.abi.Field[pt.abi.Uint64]
    asset_amount: pt.abi.Field[pt.abi.Uint64]
    asset_fraction_price: pt.abi.Field[pt.abi.Uint64]


class FracticSellOrder(pt.abi.NamedTuple):
    creator: pt.abi.Field[pt.abi.Address]
    asset_id: pt.abi.Field[pt.abi.Uint64]
    asset_amount: pt.abi.Field[pt.abi.Uint64]
    asset_fraction_price: pt.abi.Field[pt.abi.Uint64]


class MappingState:
    fractic_distribution_address = pt.TealType.bytes
    buy_orders = BoxMapping(pt.abi.Uint64, FracticBuyOrder)
    sell_orders = BoxMapping(pt.abi.Uint64, FracticSellOrder)
