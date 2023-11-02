import beaker
import pyteal as pt
from algokit_utils import DELETABLE_TEMPLATE_NAME, UPDATABLE_TEMPLATE_NAME
from smart_contracts.fractmarket.data_utils import FracticBuyOrder, MappingState

app = beaker.Application(
    "fracticmarket",
    descr="Fractic Market Main Contract",
    state=MappingState(),
)


@app.update(authorize=beaker.Authorize.only_creator(), bare=True)
def update() -> pt.Expr:
    return pt.Assert(
        pt.Tmpl.Int(UPDATABLE_TEMPLATE_NAME),
        comment="Check app is updatable",
    )


@app.delete(authorize=beaker.Authorize.only_creator(), bare=True)
def delete() -> pt.Expr:
    return pt.Assert(
        pt.Tmpl.Int(DELETABLE_TEMPLATE_NAME),
        comment="Check app is deletable",
    )


@app.external
def create_buy_order(
    deposit_payment_txn: pt.abi.PaymentTransaction,
    order_id: pt.abi.Uint64,
    asset_id: pt.abi.Uint64,
    asset_amount: pt.abi.Uint64,
    asset_fraction_price: pt.abi.Uint64,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    return pt.Seq(
        pt.Assert(pt.Not(app.state.buy_orders[pt.Itob(order_id.get())].exists())),
        pt.Assert(pt.Not(app.state.sell_orders[pt.Itob(order_id.get())].exists())),
        # pt.Assert(pt.AssetParam.creator(asset_id.get()) == app.state.fractic_distribution_address),
        pt.Assert(deposit_payment_txn.get().sender() == pt.Txn.sender()),
        pt.Assert(
            deposit_payment_txn.get().receiver()
            == pt.Global.current_application_address()
        ),
        pt.Assert(
            deposit_payment_txn.get().amount()
            == asset_amount.get() * asset_fraction_price.get()
        ),
        (addr := pt.abi.make(pt.abi.Address)).set(pt.Txn.sender()),
        (new_buy_order := FracticBuyOrder()).set(
            addr, asset_id, asset_amount, asset_fraction_price
        ),
        (app.state.buy_orders[pt.Itob(order_id.get())]).set(new_buy_order),
        (output.set(True)),
    )
