from beaker import GlobalStateValue
from beaker.lib.storage import BoxMapping
import pyteal as pt


class Proposal(pt.abi.NamedTuple):
    name: pt.abi.Field[pt.abi.String]
    url: pt.abi.Field[pt.abi.String]
    voting_start: pt.abi.Field[pt.abi.Uint64]
    voting_end: pt.abi.Field[pt.abi.Uint64]
    yes: pt.abi.Field[pt.abi.Uint64]
    no: pt.abi.Field[pt.abi.Uint64]
    abstain: pt.abi.Field[pt.abi.Uint64]


class State:
    curr_id = GlobalStateValue(pt.TealType.uint64, default=pt.Int(0))
    gov = GlobalStateValue(pt.TealType.uint64)
    min_support = GlobalStateValue(pt.TealType.uint64)
    min_duration = GlobalStateValue(pt.TealType.uint64)
    max_duration = GlobalStateValue(pt.TealType.uint64)
    proposals = BoxMapping(pt.abi.Uint64, Proposal)
    deposits = BoxMapping(pt.abi.Address, pt.abi.Uint64)
