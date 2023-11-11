import beaker
import pyteal as pt
from algokit_utils import DELETABLE_TEMPLATE_NAME, UPDATABLE_TEMPLATE_NAME
from .data_utils import MappingState, AlgolenListing, AlgolenRent


DAY_IN_SECONDS = 86_400
LISTING_FEE_MICROALGO = 1_000_000
# this should cover the asset return transaction fee
DELIST_FEE_MICROALGO = 1_000

app = beaker.Application(
    "algolen",
    descr="Algolen Contract",
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
def list_nft(
    assert_transfer_txn: pt.abi.AssetTransferTransaction,
    deposit: pt.abi.Uint64,
    price_per_day: pt.abi.Uint64,
    max_duration_in_days: pt.abi.Uint64,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    asset_owner = pt.abi.make(pt.abi.Address)
    asset_id = pt.abi.make(pt.abi.Uint64)
    return pt.Seq(
        pt.Assert(pt.Txn.assets[0] == assert_transfer_txn.get().xfer_asset()),
        asset_id.set(pt.Txn.assets[0]),
        asset_owner.set(pt.Txn.sender()),
        (new_listing := AlgolenListing()).set(
            asset_id, deposit, price_per_day, max_duration_in_days, asset_owner
        ),
        (app.state.listings[pt.Itob(asset_id.get())]).set(new_listing),
        (output.set(True)),
    )


@app.external
def delist_nft(
    fee_payment_txn: pt.abi.PaymentTransaction,
    asset_id: pt.abi.Uint64,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    asset = asset_id.get()
    listing = AlgolenListing()
    owner = pt.abi.Address()
    return pt.Seq(
        pt.Assert(
            fee_payment_txn.get().receiver() == pt.Global.current_application_address()
        ),
        pt.Assert(fee_payment_txn.get().amount() == pt.Int(DELIST_FEE_MICROALGO)),
        (app.state.listings[pt.Itob(asset)].store_into(listing)),
        (listing.owner.store_into(owner)),
        pt.Assert(owner.get() == pt.Txn.sender()),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                pt.TxnField.asset_amount: pt.Int(1),
                pt.TxnField.asset_receiver: pt.Txn.sender(),
                pt.TxnField.xfer_asset: asset,
            }
        ),
        pt.Assert(app.state.listings[pt.Itob(asset)].delete()),
        (output.set(True)),
    )


@app.external
def opt_in_to_asset(
    deposit_payment_txn: pt.abi.PaymentTransaction, *, output: pt.abi.Bool
) -> pt.Expr:
    """
    An opt-in contract method

    One time payment of LISTING_FEE_MICROALGO amount that covers opt in and box creation expenses for this nft and a small fee for the platform usage
    This fee is to be paid per NFT and permanently enables the listing of this NFT
    """
    return pt.Seq(
        pt.Assert(pt.Not(pt.Txn.assets.length() == pt.Int(0))),
        (decimals := pt.AssetParam.decimals(pt.Txn.assets[0])),
        pt.Assert(decimals.hasValue()),
        pt.Assert(decimals.value() == pt.Int(0)),
        (total := pt.AssetParam.total(pt.Txn.assets[0])),
        pt.Assert(total.hasValue()),
        pt.Assert(total.value() == pt.Int(1)),
        pt.Assert(deposit_payment_txn.get().sender() == pt.Txn.sender()),
        pt.Assert(
            deposit_payment_txn.get().receiver()
            == pt.Global.current_application_address()
        ),
        pt.Assert(deposit_payment_txn.get().amount() == pt.Int(LISTING_FEE_MICROALGO)),
        # Opt-in transaction
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                pt.TxnField.asset_amount: pt.Int(0),
                pt.TxnField.asset_receiver: pt.Global.current_application_address(),
                pt.TxnField.xfer_asset: pt.Txn.assets[0],
            }
        ),
        (output.set(True)),
    )
