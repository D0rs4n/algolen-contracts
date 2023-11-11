import beaker
import pyteal as pt
from algokit_utils import DELETABLE_TEMPLATE_NAME, UPDATABLE_TEMPLATE_NAME
from .data_utils import MappingState, AlgolenListing, AlgolenRent


MONTH_IN_SECONDS = 2_630_000
DEPOSIT_AMMOUNT = 100_000

app = beaker.Application(
    "algolenmain",
    descr="Algolen Distribution Main Contract",
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
def init_algolen_nft_flow(
    assert_transfer_txn: pt.abi.AssetTransferTransaction,
    estimated_price_in_microalgos: pt.abi.Uint64,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    """
    The entry contract method for Algolen

    It takes an AssetTransferTransaction as a parameter,
    checks if the contract is opted into the NFT, (implying checks were done previously)
    then locks the NFT into the contract's account, and creates a pool
    """

    asset_owner = pt.abi.make(pt.abi.Address)
    asset_id = pt.abi.make(pt.abi.Uint64)
    available_for_rent = pt.abi.make(pt.abi.Bool)
    return pt.Seq(
        pt.Assert(pt.Txn.assets[0] == assert_transfer_txn.get().xfer_asset()),
        pt.Assert(app.state.deposits[pt.Itob(pt.Txn.assets[0])].exists()),
        pt.Assert(
            app.state.deposits[pt.Itob(pt.Txn.assets[0])].get() == pt.Txn.sender()
        ),
        asset_id.set(pt.Txn.assets[0].index),
        asset_owner.set(pt.Txn.sender()),
        (available_for_rent.set(True)),
        (new_listing := AlgolenListing()).set(
            asset_id, estimated_price_in_microalgos, asset_owner, available_for_rent
        ),
        (app.state.listings[pt.Itob(pt.Txn.assets[0])]).set(new_listing),
        (output.set(True)),
    )


@app.external
def opt_in_to_asset(
    deposit_payment_txn: pt.abi.PaymentTransaction, *, output: pt.abi.Bool
) -> pt.Expr:
    """
    An opt-in contract method

    That will make the contract to opt-in to an NFT asset,
    if the asset is valid for Fractic, which means decimals is 0, and total is 1
    provided that the 5 Algo deposit is supplied
    """
    return pt.Seq(
        pt.Assert(pt.Not(app.state.deposits[pt.Itob(pt.Txn.assets[0])].exists())),
        pt.Assert(pt.Not(pt.Txn.assets.length() == pt.Int(0))),
        (decimals := pt.AssetParam.decimals(pt.Txn.assets[0])),
        pt.Assert(decimals.hasValue()),
        pt.Assert(decimals.value() == pt.Int(0)),
        (total := pt.AssetParam.total(pt.Txn.assets[0])),
        pt.Assert(total.hasValue()),
        pt.Assert(total.value() == pt.Int(1)),
        (creator := pt.AssetParam.creator(pt.Txn.assets[0])),
        pt.Assert(creator.hasValue()),
        pt.Assert(creator.value() == pt.Txn.sender()),
        pt.Assert(deposit_payment_txn.get().sender() == pt.Txn.sender()),
        pt.Assert(
            deposit_payment_txn.get().receiver()
            == pt.Global.current_application_address()
        ),
        # the Deposit is 5 Algos = 5000000 microAlgos
        pt.Assert(deposit_payment_txn.get().amount() == pt.Int(DEPOSIT_AMMOUNT)),
        # Record the deposit
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                pt.TxnField.asset_amount: pt.Int(0),
                pt.TxnField.asset_receiver: pt.Global.current_application_address(),
                pt.TxnField.xfer_asset: pt.Txn.assets[0],
            }
        ),
        (app.state.deposits[pt.Itob(pt.Txn.assets[0])].set(pt.Txn.sender())),
        (output.set(True)),
    )


@app.external
def deposit_into_nft(
    payment_txn: pt.abi.PaymentTransaction,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    listing = AlgolenListing()
    current_blocktime = pt.abi.make(pt.abi.Uint64)
    price = pt.abi.make(pt.abi.Uint64)
    asset_owner = pt.abi.make(pt.abi.Address)
    asset_renter = pt.abi.make(pt.abi.Address)
    next_rent_due_timestamp = pt.abi.make(pt.abi.Uint64)
    return pt.Seq(
        pt.Assert(app.state.deposits[pt.Itob(pt.Txn.assets[0])].exists()),
        app.state.listings[pt.Itob(pt.Txn.assets[0])].store_into(listing),
        (listing.estimated_price_in_microalgos.store_into(price)),
        (listing.owner.store_into(asset_owner)),
        (asset_renter.set(pt.Txn.sender())),
        pt.Assert(payment_txn.get().amount() == price.get()),
        (current_blocktime.set(pt.Txn.first_valid_time())),
        (
            next_rent_due_timestamp.set(
                pt.Int(MONTH_IN_SECONDS) + pt.Txn.first_valid_time()
            )
        ),
        (new_rent := AlgolenRent()).set(
            next_rent_due_timestamp,
            asset_owner,
            asset_renter,
        ),
        (app.state.rents[pt.Itob(pt.Txn.assets[0])]).set(new_rent),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                pt.TxnField.asset_amount: pt.Int(1),
                pt.TxnField.asset_receiver: asset_renter,
                pt.TxnField.xfer_asset: pt.Txn.assets[0],
                pt.TxnField.note: pt.Bytes("Algolen NFT Lending Protocol"),
            }
        ),
        output.set(True),
    )
