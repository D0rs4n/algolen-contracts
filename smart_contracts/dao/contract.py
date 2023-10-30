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
