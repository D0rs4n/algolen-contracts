import beaker
import pyteal as pt
from algokit_utils import DELETABLE_TEMPLATE_NAME, UPDATABLE_TEMPLATE_NAME
from .data_utils import MappingState


app = beaker.Application(
    "fractdistribution",
    descr="Fractic Distribution Main Contract",
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
def init_fractic_nft_flow(
    assert_transfer_txn: pt.abi.AssetTransferTransaction,
) -> pt.Expr:
    """
    The entry contract method for Fractic

    It takes an AssetTransferTransaction as a parameter,
    checks if the contract is opted into the NFT, (implying checks were done previously)
    then locks the NFT into the contract's account, and creates a pool
    """
    return pt.Seq()


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
        # the Deposit is 5 Algos = 5000000 microAlgos
        pt.Assert(deposit_payment_txn.get().amount() == pt.Int(5000000)),
        # Record the deposit
        (app.state.deposits[pt.Itob(pt.Txn.assets[0])].set(pt.Txn.sender())),
        (output.set(True)),
    )
