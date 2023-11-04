import beaker
import pyteal as pt
from algokit_utils import DELETABLE_TEMPLATE_NAME, UPDATABLE_TEMPLATE_NAME
from .data_utils import MappingState, FracticNFTPool

TMP_DAO_ADDR = "TMPL_DAOADDRESS"


app = beaker.Application(
    "fracticdistribution",
    descr="Fractic Distribution Main Contract",
    state=MappingState(),
)


@app.create
def create() -> pt.Expr:
    return pt.Seq(
        app.state.dao.set(pt.Tmpl.Addr(TMP_DAO_ADDR)),
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
def init_fractic_nft_flow(
    assert_transfer_txn: pt.abi.AssetTransferTransaction,
    time_limit: pt.abi.Uint64,
    max_fraction: pt.abi.Uint64,
    price_per_fraction: pt.abi.Uint64,
    *,
    output: pt.abi.Bool,
) -> pt.Expr:
    """
    The entry contract method for Fractic

    It takes an AssetTransferTransaction as a parameter,
    checks if the contract is opted into the NFT, (implying checks were done previously)
    then locks the NFT into the contract's account, and creates a pool
    """
    return pt.Seq(
        pt.Assert(max_fraction.get() <= pt.Int(100)),
        pt.Assert(pt.Txn.assets[0] == assert_transfer_txn.get().xfer_asset()),
        pt.Assert(app.state.deposits[pt.Itob(pt.Txn.assets[0])].exists()),
        pt.Assert(
            app.state.deposits[pt.Itob(pt.Txn.assets[0])].get() == pt.Txn.sender()
        ),
        (addr := pt.abi.make(pt.abi.Address)).set(pt.Txn.sender()),
        (asset_id := pt.abi.make(pt.abi.Uint64)).set(pt.Txn.assets[0].index),
        (original_asset_url := pt.AssetParam.url(pt.Txn.assets[0])),
        pt.Assert(original_asset_url.hasValue()),
        (original_asset_hash := pt.AssetParam.metadataHash(pt.Txn.assets[0])),
        pt.Assert(original_asset_hash.hasValue()),
        pt.InnerTxnBuilder.Execute(
            {
                pt.TxnField.type_enum: pt.TxnType.AssetConfig,
                pt.TxnField.config_asset_default_frozen: pt.Int(0),
                pt.TxnField.config_asset_unit_name: pt.Bytes("FRC"),
                pt.TxnField.config_asset_manager: pt.Global.current_application_address(),
                pt.TxnField.config_asset_reserve: pt.Global.current_application_address(),
                pt.TxnField.config_asset_clawback: pt.Global.current_application_address(),
                pt.TxnField.config_asset_total: max_fraction.get(),
                pt.TxnField.config_asset_decimals: pt.Int(0),
                pt.TxnField.config_asset_url: original_asset_url.value(),
                pt.TxnField.config_asset_metadata_hash: original_asset_hash.value(),
                pt.TxnField.note: pt.Bytes('{"standard": "arc69"}'),
            }
        ),
        (asset_id := pt.abi.make(pt.abi.Uint64)).set(pt.InnerTxn.created_asset_id()),
        (new_pool := FracticNFTPool()).set(
            time_limit, addr, max_fraction, asset_id, price_per_fraction
        ),
        (app.state.pools[pt.Itob(pt.Txn.assets[0])]).set(new_pool),
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
        pt.Assert(deposit_payment_txn.get().amount() == pt.Int(100000)),
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
def buy_nft_fraction() -> pt.Expr:
    return pt.Seq(
        (
            balance := pt.AssetHolding.balance(
                pt.Global.current_application_address(), pt.Txn.assets[0]
            )
        ),
        pt.Assert(balance.value() > pt.Int(0)),
    )
