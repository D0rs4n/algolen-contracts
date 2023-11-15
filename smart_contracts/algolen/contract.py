import beaker
import pyteal as pt
from algokit_utils import DELETABLE_TEMPLATE_NAME, UPDATABLE_TEMPLATE_NAME
from .data_utils import MappingState, AlgolenListing, AlgolenRent


DAY_IN_SECONDS = 86_400
LISTING_FEE_MICROALGO = 1_000_000

# this pays for asset transfer to owner
DELIST_FEE_MICROALGO = 1_000

# this pays for 4 transactions:
# asset to renter
# profit to lender
#
# asset to lender
# deposit to renter
# or
# deposit to lender
RENT_FEE_MICROALGO = 4_000

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
    asset_transfer_txn: pt.abi.AssetTransferTransaction,
    deposit: pt.abi.Uint64,
    price_per_day: pt.abi.Uint64,
    max_duration_in_days: pt.abi.Uint64,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    asset_id = pt.Txn.assets[0]
    asset_owner = pt.abi.make(pt.abi.Address)
    return pt.Seq(
        pt.Assert(price_per_day.get() > pt.Int(0)),
        pt.Assert(deposit.get() > pt.Int(0)),
        pt.Assert(pt.Txn.assets[0] == asset_transfer_txn.get().xfer_asset()),
        asset_owner.set(pt.Txn.sender()),
        (new_listing := AlgolenListing()).set(
            deposit, price_per_day, max_duration_in_days, asset_owner
        ),
        (app.state.listings[pt.Itob(asset_id)]).set(new_listing),
        (output.set(True)),
    )


@app.external
def delist_nft(
    fee_payment_txn: pt.abi.PaymentTransaction,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    asset_id = pt.Txn.assets[0]
    listing = AlgolenListing()
    owner = pt.abi.Address()
    return pt.Seq(
        pt.Assert(
            fee_payment_txn.get().receiver() == pt.Global.current_application_address()
        ),
        pt.Assert(fee_payment_txn.get().amount() == pt.Int(DELIST_FEE_MICROALGO)),
        (app.state.listings[pt.Itob(asset_id)].store_into(listing)),
        (listing.owner.store_into(owner)),
        pt.Assert(owner.get() == pt.Txn.sender()),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                pt.TxnField.asset_amount: pt.Int(1),
                pt.TxnField.asset_receiver: pt.Txn.sender(),
                pt.TxnField.xfer_asset: asset_id,
            }
        ),
        pt.Assert(app.state.listings[pt.Itob(asset_id)].delete()),
        (output.set(True)),
    )


@app.external
def opt_in_to_asset(
    deposit_payment_txn: pt.abi.PaymentTransaction, *, output: pt.abi.Bool
) -> pt.Expr:
    """
    An opt-in contract method

    One time payment of LISTING_FEE_MICROALGO amount
    covers opt in, box creation for this nft and a small fee for the platform usage
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


@app.external
def rent_nft(
    payment_txn: pt.abi.PaymentTransaction,
    duration_in_days: pt.abi.Uint64,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    asset_id = pt.Txn.assets[0]
    listing = AlgolenListing()
    deposit = pt.abi.make(pt.abi.Uint64)
    price_per_day = pt.abi.make(pt.abi.Uint64)
    max_duration_in_days = pt.abi.make(pt.abi.Uint64)
    asset_owner = pt.abi.make(pt.abi.Address)
    asset_renter = pt.abi.make(pt.abi.Address)
    end_date = pt.abi.make(pt.abi.Uint64)
    return pt.Seq(
        app.state.listings[pt.Itob(pt.Txn.assets[0])].store_into(listing),
        (listing.deposit.store_into(deposit)),
        (listing.price_per_day.store_into(price_per_day)),
        (listing.max_duration_in_days.store_into(max_duration_in_days)),
        (listing.owner.store_into(asset_owner)),
        (asset_renter.set(pt.Txn.sender())),
        pt.Assert(duration_in_days.get() > pt.Int(0)),
        pt.Assert(max_duration_in_days.get() >= duration_in_days.get()),
        pt.Assert(
            payment_txn.get().amount()
            == deposit.get()
            + (duration_in_days.get() * price_per_day.get())
            + pt.Int(RENT_FEE_MICROALGO)
        ),
        (
            end_date.set(
                (pt.Int(DAY_IN_SECONDS) * duration_in_days.get())
                + pt.Txn.first_valid_time()
            )
        ),
        (new_rent := AlgolenRent()).set(
            end_date,
            deposit,
            asset_owner,
            asset_renter,
        ),
        pt.Assert(app.state.listings[pt.Itob(asset_id)].delete()),
        (app.state.rents[pt.Itob(asset_id)]).set(new_rent),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                pt.TxnField.asset_amount: pt.Int(1),
                pt.TxnField.asset_receiver: asset_renter.get(),
                pt.TxnField.xfer_asset: asset_id,
            }
        ),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.Payment,
                pt.TxnField.amount: (duration_in_days.get() * price_per_day.get()),
                pt.TxnField.receiver: asset_owner.get(),
            }
        ),
        output.set(True),
    )


@app.external
def return_nft(
    asset_transfer_txn: pt.abi.AssetTransferTransaction,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    asset_id = pt.Txn.assets[0]
    rent = AlgolenRent()
    deposit = pt.abi.make(pt.abi.Uint64)
    end_date = pt.abi.make(pt.abi.Uint64)
    asset_owner = pt.abi.make(pt.abi.Address)
    asset_renter = pt.abi.make(pt.abi.Address)
    return pt.Seq(
        pt.Assert(pt.Txn.assets[0] == asset_transfer_txn.get().xfer_asset()),
        app.state.rents[pt.Itob(asset_id)].store_into(rent),
        (rent.deposit.store_into(deposit)),
        (rent.end_date.store_into(end_date)),
        (rent.asset_owner.store_into(asset_owner)),
        (rent.asset_renter.store_into(asset_renter)),
        pt.Assert(pt.Txn.first_valid_time() < end_date.get()),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.Payment,
                pt.TxnField.amount: deposit.get(),
                pt.TxnField.receiver: pt.Txn.sender(),
            }
        ),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                pt.TxnField.asset_amount: pt.Int(1),
                pt.TxnField.asset_receiver: asset_owner.get(),
                pt.TxnField.xfer_asset: asset_id,
            }
        ),
        pt.Assert(app.state.rents[pt.Itob(asset_id)].delete()),
        output.set(True),
    )


@app.external
def claim_deposit(
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    asset_id = pt.Txn.assets[0]
    rent = AlgolenRent()
    deposit = pt.abi.make(pt.abi.Uint64)
    end_date = pt.abi.make(pt.abi.Uint64)
    asset_owner = pt.abi.make(pt.abi.Address)
    return pt.Seq(
        app.state.rents[pt.Itob(asset_id)].store_into(rent),
        (rent.deposit.store_into(deposit)),
        (rent.end_date.store_into(end_date)),
        (rent.asset_owner.store_into(asset_owner)),
        pt.Assert(asset_owner.get() == pt.Txn.sender()),
        pt.Assert(pt.Txn.first_valid_time() > end_date.get()),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.Payment,
                pt.TxnField.amount: deposit.get(),
                pt.TxnField.receiver: asset_owner.get(),
            }
        ),
        pt.Assert(app.state.rents[pt.Itob(asset_id)].delete()),
        output.set(True),
    )
