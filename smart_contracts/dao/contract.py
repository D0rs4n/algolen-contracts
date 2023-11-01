import beaker
import pyteal as pt
from algokit_utils import DELETABLE_TEMPLATE_NAME, UPDATABLE_TEMPLATE_NAME
from .data_utils import State, Proposal

app = beaker.Application("dao", state=State)


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


@app.create(bare=True)
def create() -> pt.Expr:
    return pt.Seq(
        app.initialize_global_state(),
        # app.state.gov.set(gov.get()),
    )


@app.external()
def set_gov(
    gov: pt.abi.Uint64,
) -> pt.Expr:
    return pt.Seq(
        app.state.gov.set(gov.get()),
    )


@app.external()
def gov_opt_in(*, output: pt.abi.Bool) -> pt.Expr:
    """
    An opt-in contract method

    That will make the contract to opt-in to the gov token of the contract,
    """
    return pt.Seq(
        [
            pt.Assert(
                pt.And(
                    pt.Global.group_size() == pt.Int(2),
                )
            ),
            pt.InnerTxnBuilder.Execute(
                {
                    pt.TxnField.type_enum: pt.TxnType.AssetTransfer,
                    pt.TxnField.xfer_asset: app.state.gov.get(),
                    pt.TxnField.asset_receiver: pt.Global.current_application_address(),
                    pt.TxnField.asset_amount: pt.Int(0),
                }
            ),
            output.set(True),
        ]
    )


@app.external
def deposit(txn: pt.abi.AssetTransferTransaction, *, output: pt.abi.Bool) -> pt.Expr:
    """
    An deposit contract method

    That will check whether the deposit is valid,
    and store the deposit in the contract's state
    """
    return pt.Seq(
        pt.Assert(txn.get().xfer_asset() == app.state.gov.get()),
        pt.Assert(txn.get().sender() == txn.get().asset_sender()),
        pt.Assert(
            txn.get().asset_receiver() == pt.Global.current_application_address()
        ),
        app.state.deposits[txn.get().sender()].set(pt.Itob(txn.get().asset_amount())),
        output.set(True),
    )


@app.external
def add_proposal(proposal: Proposal) -> pt.Expr:
    curr_id = app.state.curr_id.get()
    new_id = curr_id + pt.Int(1)

    return pt.Seq(
        app.state.proposals[curr_id].set(proposal),
        app.state.curr_id.set(new_id),
    )


@app.external
def hello(name: pt.abi.String, *, output: pt.abi.String) -> pt.Expr:
    return output.set(pt.Concat(pt.Bytes("Hello, "), name.get()))
