# flake8: noqa
# fmt: off
# mypy: disable-error-code="no-any-return, no-untyped-call"
# This file was automatically generated by algokit-client-generator.
# DO NOT MODIFY IT BY HAND.
# requires: algokit-utils@^1.2.0
import base64
import dataclasses
import decimal
import typing
from abc import ABC, abstractmethod

import algokit_utils
import algosdk
from algosdk.atomic_transaction_composer import (
    AtomicTransactionComposer,
    AtomicTransactionResponse,
    TransactionSigner,
    TransactionWithSigner
)

_APP_SPEC_JSON = r"""{
    "hints": {
        "create(address)void": {
            "call_config": {
                "no_op": "CREATE"
            }
        },
        "init_fractic_nft_flow(axfer,uint64,uint64,uint64)bool": {
            "call_config": {
                "no_op": "CALL"
            }
        },
        "opt_in_to_asset(pay)bool": {
            "call_config": {
                "no_op": "CALL"
            }
        },
        "buy_nft_fraction()void": {
            "call_config": {
                "no_op": "CALL"
            }
        }
    },
    "source": {
        "approval": "I3ByYWdtYSB2ZXJzaW9uIDgKaW50Y2Jsb2NrIDAgMSA0CmJ5dGVjYmxvY2sgMHg2NCAweCAweDcwIDB4MTUxZjdjNzUgMHgwMAp0eG4gTnVtQXBwQXJncwppbnRjXzAgLy8gMAo9PQpibnogbWFpbl9sMTAKdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMApwdXNoYnl0ZXMgMHhjYzY5NGVhYSAvLyAiY3JlYXRlKGFkZHJlc3Mpdm9pZCIKPT0KYm56IG1haW5fbDkKdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMApwdXNoYnl0ZXMgMHg5OGMwMjllMyAvLyAiaW5pdF9mcmFjdGljX25mdF9mbG93KGF4ZmVyLHVpbnQ2NCx1aW50NjQsdWludDY0KWJvb2wiCj09CmJueiBtYWluX2w4CnR4bmEgQXBwbGljYXRpb25BcmdzIDAKcHVzaGJ5dGVzIDB4MmVkZWYxMTIgLy8gIm9wdF9pbl90b19hc3NldChwYXkpYm9vbCIKPT0KYm56IG1haW5fbDcKdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMApwdXNoYnl0ZXMgMHhjMTA4MDUxZiAvLyAiYnV5X25mdF9mcmFjdGlvbigpdm9pZCIKPT0KYm56IG1haW5fbDYKZXJyCm1haW5fbDY6CnR4biBPbkNvbXBsZXRpb24KaW50Y18wIC8vIE5vT3AKPT0KdHhuIEFwcGxpY2F0aW9uSUQKaW50Y18wIC8vIDAKIT0KJiYKYXNzZXJ0CmNhbGxzdWIgYnV5bmZ0ZnJhY3Rpb25jYXN0ZXJfOQppbnRjXzEgLy8gMQpyZXR1cm4KbWFpbl9sNzoKdHhuIE9uQ29tcGxldGlvbgppbnRjXzAgLy8gTm9PcAo9PQp0eG4gQXBwbGljYXRpb25JRAppbnRjXzAgLy8gMAohPQomJgphc3NlcnQKY2FsbHN1YiBvcHRpbnRvYXNzZXRjYXN0ZXJfOAppbnRjXzEgLy8gMQpyZXR1cm4KbWFpbl9sODoKdHhuIE9uQ29tcGxldGlvbgppbnRjXzAgLy8gTm9PcAo9PQp0eG4gQXBwbGljYXRpb25JRAppbnRjXzAgLy8gMAohPQomJgphc3NlcnQKY2FsbHN1YiBpbml0ZnJhY3RpY25mdGZsb3djYXN0ZXJfNwppbnRjXzEgLy8gMQpyZXR1cm4KbWFpbl9sOToKdHhuIE9uQ29tcGxldGlvbgppbnRjXzAgLy8gTm9PcAo9PQp0eG4gQXBwbGljYXRpb25JRAppbnRjXzAgLy8gMAo9PQomJgphc3NlcnQKY2FsbHN1YiBjcmVhdGVjYXN0ZXJfNgppbnRjXzEgLy8gMQpyZXR1cm4KbWFpbl9sMTA6CnR4biBPbkNvbXBsZXRpb24KaW50Y18yIC8vIFVwZGF0ZUFwcGxpY2F0aW9uCj09CmJueiBtYWluX2wxNAp0eG4gT25Db21wbGV0aW9uCnB1c2hpbnQgNSAvLyBEZWxldGVBcHBsaWNhdGlvbgo9PQpibnogbWFpbl9sMTMKZXJyCm1haW5fbDEzOgp0eG4gQXBwbGljYXRpb25JRAppbnRjXzAgLy8gMAohPQphc3NlcnQKY2FsbHN1YiBkZWxldGVfMgppbnRjXzEgLy8gMQpyZXR1cm4KbWFpbl9sMTQ6CnR4biBBcHBsaWNhdGlvbklECmludGNfMCAvLyAwCiE9CmFzc2VydApjYWxsc3ViIHVwZGF0ZV8xCmludGNfMSAvLyAxCnJldHVybgoKLy8gY3JlYXRlCmNyZWF0ZV8wOgpwcm90byAxIDAKcHVzaGJ5dGVzIDB4NjQ2MTZmIC8vICJkYW8iCmZyYW1lX2RpZyAtMQphcHBfZ2xvYmFsX3B1dApyZXRzdWIKCi8vIHVwZGF0ZQp1cGRhdGVfMToKcHJvdG8gMCAwCnR4biBTZW5kZXIKZ2xvYmFsIENyZWF0b3JBZGRyZXNzCj09Ci8vIHVuYXV0aG9yaXplZAphc3NlcnQKcHVzaGludCBUTVBMX1VQREFUQUJMRSAvLyBUTVBMX1VQREFUQUJMRQovLyBDaGVjayBhcHAgaXMgdXBkYXRhYmxlCmFzc2VydApyZXRzdWIKCi8vIGRlbGV0ZQpkZWxldGVfMjoKcHJvdG8gMCAwCnR4biBTZW5kZXIKZ2xvYmFsIENyZWF0b3JBZGRyZXNzCj09Ci8vIHVuYXV0aG9yaXplZAphc3NlcnQKcHVzaGludCBUTVBMX0RFTEVUQUJMRSAvLyBUTVBMX0RFTEVUQUJMRQovLyBDaGVjayBhcHAgaXMgZGVsZXRhYmxlCmFzc2VydApyZXRzdWIKCi8vIGluaXRfZnJhY3RpY19uZnRfZmxvdwppbml0ZnJhY3RpY25mdGZsb3dfMzoKcHJvdG8gNCAxCmludGNfMCAvLyAwCmJ5dGVjXzEgLy8gIiIKaW50Y18wIC8vIDAKZHVwCmJ5dGVjXzEgLy8gIiIKaW50Y18wIC8vIDAKZHVwCmJ5dGVjXzEgLy8gIiIKZHVwCmZyYW1lX2RpZyAtMgpwdXNoaW50IDEwMCAvLyAxMDAKPD0KYXNzZXJ0CnR4bmEgQXNzZXRzIDAKZnJhbWVfZGlnIC00Cmd0eG5zIFhmZXJBc3NldAo9PQphc3NlcnQKYnl0ZWNfMCAvLyAiZCIKdHhuYSBBc3NldHMgMAppdG9iCmNvbmNhdApib3hfbGVuCnN0b3JlIDEKc3RvcmUgMApsb2FkIDEKYXNzZXJ0CmJ5dGVjXzAgLy8gImQiCnR4bmEgQXNzZXRzIDAKaXRvYgpjb25jYXQKYm94X2dldApzdG9yZSAzCnN0b3JlIDIKbG9hZCAzCmFzc2VydApsb2FkIDIKdHhuIFNlbmRlcgo9PQphc3NlcnQKdHhuIFNlbmRlcgpmcmFtZV9idXJ5IDEKZnJhbWVfZGlnIDEKbGVuCnB1c2hpbnQgMzIgLy8gMzIKPT0KYXNzZXJ0CmludGNfMCAvLyAwCmZyYW1lX2J1cnkgMgp0eG5hIEFzc2V0cyAwCmFzc2V0X3BhcmFtc19nZXQgQXNzZXRVUkwKc3RvcmUgNQpzdG9yZSA0CmxvYWQgNQphc3NlcnQKdHhuYSBBc3NldHMgMAphc3NldF9wYXJhbXNfZ2V0IEFzc2V0TWV0YWRhdGFIYXNoCnN0b3JlIDcKc3RvcmUgNgpsb2FkIDcKYXNzZXJ0Cml0eG5fYmVnaW4KcHVzaGludCAzIC8vIGFjZmcKaXR4bl9maWVsZCBUeXBlRW51bQppbnRjXzAgLy8gMAppdHhuX2ZpZWxkIENvbmZpZ0Fzc2V0RGVmYXVsdEZyb3plbgpwdXNoYnl0ZXMgMHg0NjUyNDMgLy8gIkZSQyIKaXR4bl9maWVsZCBDb25maWdBc3NldFVuaXROYW1lCmdsb2JhbCBDdXJyZW50QXBwbGljYXRpb25BZGRyZXNzCml0eG5fZmllbGQgQ29uZmlnQXNzZXRNYW5hZ2VyCmdsb2JhbCBDdXJyZW50QXBwbGljYXRpb25BZGRyZXNzCml0eG5fZmllbGQgQ29uZmlnQXNzZXRSZXNlcnZlCmdsb2JhbCBDdXJyZW50QXBwbGljYXRpb25BZGRyZXNzCml0eG5fZmllbGQgQ29uZmlnQXNzZXRDbGF3YmFjawpmcmFtZV9kaWcgLTIKaXR4bl9maWVsZCBDb25maWdBc3NldFRvdGFsCmludGNfMCAvLyAwCml0eG5fZmllbGQgQ29uZmlnQXNzZXREZWNpbWFscwpsb2FkIDQKaXR4bl9maWVsZCBDb25maWdBc3NldFVSTApsb2FkIDYKaXR4bl9maWVsZCBDb25maWdBc3NldE1ldGFkYXRhSGFzaApwdXNoYnl0ZXMgMHg3YjIyNzM3NDYxNmU2NDYxNzI2NDIyM2EyMDIyNjE3MjYzMzYzOTIyN2QgLy8gIntcInN0YW5kYXJkXCI6IFwiYXJjNjlcIn0iCml0eG5fZmllbGQgTm90ZQppdHhuX3N1Ym1pdAppdHhuIENyZWF0ZWRBc3NldElECmZyYW1lX2J1cnkgMwpmcmFtZV9kaWcgLTMKaXRvYgpmcmFtZV9kaWcgMQpjb25jYXQKZnJhbWVfZGlnIC0yCml0b2IKY29uY2F0CmZyYW1lX2RpZyAzCml0b2IKY29uY2F0CmZyYW1lX2RpZyAtMQppdG9iCmNvbmNhdApmcmFtZV9idXJ5IDQKYnl0ZWNfMiAvLyAicCIKdHhuYSBBc3NldHMgMAppdG9iCmNvbmNhdApib3hfZGVsCnBvcApieXRlY18yIC8vICJwIgp0eG5hIEFzc2V0cyAwCml0b2IKY29uY2F0CmZyYW1lX2RpZyA0CmJveF9wdXQKaW50Y18xIC8vIDEKZnJhbWVfYnVyeSAwCnJldHN1YgoKLy8gb3B0X2luX3RvX2Fzc2V0Cm9wdGludG9hc3NldF80Ogpwcm90byAxIDEKaW50Y18wIC8vIDAKYnl0ZWNfMCAvLyAiZCIKdHhuYSBBc3NldHMgMAppdG9iCmNvbmNhdApib3hfbGVuCnN0b3JlIDkKc3RvcmUgOApsb2FkIDkKIQphc3NlcnQKdHhuIE51bUFzc2V0cwppbnRjXzAgLy8gMAo9PQohCmFzc2VydAp0eG5hIEFzc2V0cyAwCmFzc2V0X3BhcmFtc19nZXQgQXNzZXREZWNpbWFscwpzdG9yZSAxMQpzdG9yZSAxMApsb2FkIDExCmFzc2VydApsb2FkIDEwCmludGNfMCAvLyAwCj09CmFzc2VydAp0eG5hIEFzc2V0cyAwCmFzc2V0X3BhcmFtc19nZXQgQXNzZXRUb3RhbApzdG9yZSAxMwpzdG9yZSAxMgpsb2FkIDEzCmFzc2VydApsb2FkIDEyCmludGNfMSAvLyAxCj09CmFzc2VydAp0eG5hIEFzc2V0cyAwCmFzc2V0X3BhcmFtc19nZXQgQXNzZXRDcmVhdG9yCnN0b3JlIDE1CnN0b3JlIDE0CmxvYWQgMTUKYXNzZXJ0CmxvYWQgMTQKdHhuIFNlbmRlcgo9PQphc3NlcnQKZnJhbWVfZGlnIC0xCmd0eG5zIFNlbmRlcgp0eG4gU2VuZGVyCj09CmFzc2VydApmcmFtZV9kaWcgLTEKZ3R4bnMgUmVjZWl2ZXIKZ2xvYmFsIEN1cnJlbnRBcHBsaWNhdGlvbkFkZHJlc3MKPT0KYXNzZXJ0CmZyYW1lX2RpZyAtMQpndHhucyBBbW91bnQKcHVzaGludCAxMDAwMDAgLy8gMTAwMDAwCj09CmFzc2VydAppdHhuX2JlZ2luCmludGNfMiAvLyBheGZlcgppdHhuX2ZpZWxkIFR5cGVFbnVtCmludGNfMCAvLyAwCml0eG5fZmllbGQgQXNzZXRBbW91bnQKZ2xvYmFsIEN1cnJlbnRBcHBsaWNhdGlvbkFkZHJlc3MKaXR4bl9maWVsZCBBc3NldFJlY2VpdmVyCnR4bmEgQXNzZXRzIDAKaXR4bl9maWVsZCBYZmVyQXNzZXQKaXR4bl9zdWJtaXQKYnl0ZWNfMCAvLyAiZCIKdHhuYSBBc3NldHMgMAppdG9iCmNvbmNhdApib3hfZGVsCnBvcApieXRlY18wIC8vICJkIgp0eG5hIEFzc2V0cyAwCml0b2IKY29uY2F0CnR4biBTZW5kZXIKYm94X3B1dAppbnRjXzEgLy8gMQpmcmFtZV9idXJ5IDAKcmV0c3ViCgovLyBidXlfbmZ0X2ZyYWN0aW9uCmJ1eW5mdGZyYWN0aW9uXzU6CnByb3RvIDAgMApnbG9iYWwgQ3VycmVudEFwcGxpY2F0aW9uQWRkcmVzcwp0eG5hIEFzc2V0cyAwCmFzc2V0X2hvbGRpbmdfZ2V0IEFzc2V0QmFsYW5jZQpzdG9yZSAxNgppbnRjXzAgLy8gMAo+CmFzc2VydApyZXRzdWIKCi8vIGNyZWF0ZV9jYXN0ZXIKY3JlYXRlY2FzdGVyXzY6CnByb3RvIDAgMApieXRlY18xIC8vICIiCnR4bmEgQXBwbGljYXRpb25BcmdzIDEKZnJhbWVfYnVyeSAwCmZyYW1lX2RpZyAwCmNhbGxzdWIgY3JlYXRlXzAKcmV0c3ViCgovLyBpbml0X2ZyYWN0aWNfbmZ0X2Zsb3dfY2FzdGVyCmluaXRmcmFjdGljbmZ0Zmxvd2Nhc3Rlcl83Ogpwcm90byAwIDAKaW50Y18wIC8vIDAKZHVwbiA0CnR4bmEgQXBwbGljYXRpb25BcmdzIDEKYnRvaQpmcmFtZV9idXJ5IDIKdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMgpidG9pCmZyYW1lX2J1cnkgMwp0eG5hIEFwcGxpY2F0aW9uQXJncyAzCmJ0b2kKZnJhbWVfYnVyeSA0CnR4biBHcm91cEluZGV4CmludGNfMSAvLyAxCi0KZnJhbWVfYnVyeSAxCmZyYW1lX2RpZyAxCmd0eG5zIFR5cGVFbnVtCmludGNfMiAvLyBheGZlcgo9PQphc3NlcnQKZnJhbWVfZGlnIDEKZnJhbWVfZGlnIDIKZnJhbWVfZGlnIDMKZnJhbWVfZGlnIDQKY2FsbHN1YiBpbml0ZnJhY3RpY25mdGZsb3dfMwpmcmFtZV9idXJ5IDAKYnl0ZWNfMyAvLyAweDE1MWY3Yzc1CmJ5dGVjIDQgLy8gMHgwMAppbnRjXzAgLy8gMApmcmFtZV9kaWcgMApzZXRiaXQKY29uY2F0CmxvZwpyZXRzdWIKCi8vIG9wdF9pbl90b19hc3NldF9jYXN0ZXIKb3B0aW50b2Fzc2V0Y2FzdGVyXzg6CnByb3RvIDAgMAppbnRjXzAgLy8gMApkdXAKdHhuIEdyb3VwSW5kZXgKaW50Y18xIC8vIDEKLQpmcmFtZV9idXJ5IDEKZnJhbWVfZGlnIDEKZ3R4bnMgVHlwZUVudW0KaW50Y18xIC8vIHBheQo9PQphc3NlcnQKZnJhbWVfZGlnIDEKY2FsbHN1YiBvcHRpbnRvYXNzZXRfNApmcmFtZV9idXJ5IDAKYnl0ZWNfMyAvLyAweDE1MWY3Yzc1CmJ5dGVjIDQgLy8gMHgwMAppbnRjXzAgLy8gMApmcmFtZV9kaWcgMApzZXRiaXQKY29uY2F0CmxvZwpyZXRzdWIKCi8vIGJ1eV9uZnRfZnJhY3Rpb25fY2FzdGVyCmJ1eW5mdGZyYWN0aW9uY2FzdGVyXzk6CnByb3RvIDAgMApjYWxsc3ViIGJ1eW5mdGZyYWN0aW9uXzUKcmV0c3Vi",
        "clear": "I3ByYWdtYSB2ZXJzaW9uIDgKcHVzaGludCAwIC8vIDAKcmV0dXJu"
    },
    "state": {
        "global": {
            "num_byte_slices": 1,
            "num_uints": 0
        },
        "local": {
            "num_byte_slices": 0,
            "num_uints": 0
        }
    },
    "schema": {
        "global": {
            "declared": {
                "dao": {
                    "type": "bytes",
                    "key": "dao",
                    "descr": ""
                }
            },
            "reserved": {}
        },
        "local": {
            "declared": {},
            "reserved": {}
        }
    },
    "contract": {
        "name": "fracticdistribution",
        "methods": [
            {
                "name": "create",
                "args": [
                    {
                        "type": "address",
                        "name": "dao"
                    }
                ],
                "returns": {
                    "type": "void"
                }
            },
            {
                "name": "init_fractic_nft_flow",
                "args": [
                    {
                        "type": "axfer",
                        "name": "assert_transfer_txn"
                    },
                    {
                        "type": "uint64",
                        "name": "time_limit"
                    },
                    {
                        "type": "uint64",
                        "name": "max_fraction"
                    },
                    {
                        "type": "uint64",
                        "name": "price_per_fraction"
                    }
                ],
                "returns": {
                    "type": "bool"
                },
                "desc": "The entry contract method for Fractic\nIt takes an AssetTransferTransaction as a parameter, checks if the contract is opted into the NFT, (implying checks were done previously) then locks the NFT into the contract's account, and creates a pool"
            },
            {
                "name": "opt_in_to_asset",
                "args": [
                    {
                        "type": "pay",
                        "name": "deposit_payment_txn"
                    }
                ],
                "returns": {
                    "type": "bool"
                },
                "desc": "An opt-in contract method\nThat will make the contract to opt-in to an NFT asset, if the asset is valid for Fractic, which means decimals is 0, and total is 1 provided that the 5 Algo deposit is supplied"
            },
            {
                "name": "buy_nft_fraction",
                "args": [],
                "returns": {
                    "type": "void"
                }
            }
        ],
        "networks": {},
        "desc": "Fractic Distribution Main Contract"
    },
    "bare_call_config": {
        "delete_application": "CALL",
        "update_application": "CALL"
    }
}"""
APP_SPEC = algokit_utils.ApplicationSpecification.from_json(_APP_SPEC_JSON)
_TReturn = typing.TypeVar("_TReturn")


class _ArgsBase(ABC, typing.Generic[_TReturn]):
    @staticmethod
    @abstractmethod
    def method() -> str:
        ...


_TArgs = typing.TypeVar("_TArgs", bound=_ArgsBase[typing.Any])


@dataclasses.dataclass(kw_only=True)
class _TArgsHolder(typing.Generic[_TArgs]):
    args: _TArgs


@dataclasses.dataclass(kw_only=True)
class DeployCreate(algokit_utils.DeployCreateCallArgs, _TArgsHolder[_TArgs], typing.Generic[_TArgs]):
    pass


def _filter_none(value: dict | typing.Any) -> dict | typing.Any:
    if isinstance(value, dict):
        return {k: _filter_none(v) for k, v in value.items() if v is not None}
    return value


def _as_dict(data: typing.Any, *, convert_all: bool = True) -> dict[str, typing.Any]:
    if data is None:
        return {}
    if not dataclasses.is_dataclass(data):
        raise TypeError(f"{data} must be a dataclass")
    if convert_all:
        result = dataclasses.asdict(data)
    else:
        result = {f.name: getattr(data, f.name) for f in dataclasses.fields(data)}
    return _filter_none(result)


def _convert_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
) -> algokit_utils.TransactionParametersDict:
    return typing.cast(algokit_utils.TransactionParametersDict, _as_dict(transaction_parameters))


def _convert_call_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
) -> algokit_utils.OnCompleteCallParametersDict:
    return typing.cast(algokit_utils.OnCompleteCallParametersDict, _as_dict(transaction_parameters))


def _convert_create_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
    on_complete: algokit_utils.OnCompleteActionName,
) -> algokit_utils.CreateCallParametersDict:
    result = typing.cast(algokit_utils.CreateCallParametersDict, _as_dict(transaction_parameters))
    on_complete_enum = on_complete.replace("_", " ").title().replace(" ", "") + "OC"
    result["on_complete"] = getattr(algosdk.transaction.OnComplete, on_complete_enum)
    return result


def _convert_deploy_args(
    deploy_args: algokit_utils.DeployCallArgs | None,
) -> algokit_utils.ABICreateCallArgsDict | None:
    if deploy_args is None:
        return None

    deploy_args_dict = typing.cast(algokit_utils.ABICreateCallArgsDict, _as_dict(deploy_args))
    if isinstance(deploy_args, _TArgsHolder):
        deploy_args_dict["args"] = _as_dict(deploy_args.args)
        deploy_args_dict["method"] = deploy_args.args.method()

    return deploy_args_dict


@dataclasses.dataclass(kw_only=True)
class InitFracticNftFlowArgs(_ArgsBase[bool]):
    """The entry contract method for Fractic
    It takes an AssetTransferTransaction as a parameter, checks if the contract is opted into the NFT, (implying checks were done previously) then locks the NFT into the contract's account, and creates a pool"""

    assert_transfer_txn: TransactionWithSigner
    time_limit: int
    max_fraction: int
    price_per_fraction: int

    @staticmethod
    def method() -> str:
        return "init_fractic_nft_flow(axfer,uint64,uint64,uint64)bool"


@dataclasses.dataclass(kw_only=True)
class OptInToAssetArgs(_ArgsBase[bool]):
    """An opt-in contract method
    That will make the contract to opt-in to an NFT asset, if the asset is valid for Fractic, which means decimals is 0, and total is 1 provided that the 5 Algo deposit is supplied"""

    deposit_payment_txn: TransactionWithSigner

    @staticmethod
    def method() -> str:
        return "opt_in_to_asset(pay)bool"


@dataclasses.dataclass(kw_only=True)
class BuyNftFractionArgs(_ArgsBase[None]):
    @staticmethod
    def method() -> str:
        return "buy_nft_fraction()void"


@dataclasses.dataclass(kw_only=True)
class CreateArgs(_ArgsBase[None]):
    dao: str

    @staticmethod
    def method() -> str:
        return "create(address)void"


class ByteReader:
    def __init__(self, data: bytes):
        self._data = data

    @property
    def as_bytes(self) -> bytes:
        return self._data

    @property
    def as_str(self) -> str:
        return self._data.decode("utf8")

    @property
    def as_base64(self) -> str:
        return base64.b64encode(self._data).decode("utf8")

    @property
    def as_hex(self) -> str:
        return self._data.hex()


class GlobalState:
    def __init__(self, data: dict[bytes, bytes | int]):
        self.dao = ByteReader(typing.cast(bytes, data.get(b"dao")))


class Composer:

    def __init__(self, app_client: algokit_utils.ApplicationClient, atc: AtomicTransactionComposer):
        self.app_client = app_client
        self.atc = atc

    def build(self) -> AtomicTransactionComposer:
        return self.atc

    def execute(self) -> AtomicTransactionResponse:
        return self.app_client.execute_atc(self.atc)

    def init_fractic_nft_flow(
        self,
        *,
        assert_transfer_txn: TransactionWithSigner,
        time_limit: int,
        max_fraction: int,
        price_per_fraction: int,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """The entry contract method for Fractic
        It takes an AssetTransferTransaction as a parameter, checks if the contract is opted into the NFT, (implying checks were done previously) then locks the NFT into the contract's account, and creates a pool
        
        Adds a call to `init_fractic_nft_flow(axfer,uint64,uint64,uint64)bool` ABI method
        
        :param TransactionWithSigner assert_transfer_txn: The `assert_transfer_txn` ABI parameter
        :param int time_limit: The `time_limit` ABI parameter
        :param int max_fraction: The `max_fraction` ABI parameter
        :param int price_per_fraction: The `price_per_fraction` ABI parameter
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = InitFracticNftFlowArgs(
            assert_transfer_txn=assert_transfer_txn,
            time_limit=time_limit,
            max_fraction=max_fraction,
            price_per_fraction=price_per_fraction,
        )
        self.app_client.compose_call(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return self

    def opt_in_to_asset(
        self,
        *,
        deposit_payment_txn: TransactionWithSigner,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """An opt-in contract method
        That will make the contract to opt-in to an NFT asset, if the asset is valid for Fractic, which means decimals is 0, and total is 1 provided that the 5 Algo deposit is supplied
        
        Adds a call to `opt_in_to_asset(pay)bool` ABI method
        
        :param TransactionWithSigner deposit_payment_txn: The `deposit_payment_txn` ABI parameter
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = OptInToAssetArgs(
            deposit_payment_txn=deposit_payment_txn,
        )
        self.app_client.compose_call(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return self

    def buy_nft_fraction(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """Adds a call to `buy_nft_fraction()void` ABI method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = BuyNftFractionArgs()
        self.app_client.compose_call(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return self

    def create_create(
        self,
        *,
        dao: str,
        on_complete: typing.Literal["no_op"] = "no_op",
        transaction_parameters: algokit_utils.CreateTransactionParameters | None = None,
    ) -> "Composer":
        """Adds a call to `create(address)void` ABI method
        
        :param str dao: The `dao` ABI parameter
        :param typing.Literal[no_op] on_complete: On completion type to use
        :param algokit_utils.CreateTransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        args = CreateArgs(
            dao=dao,
        )
        self.app_client.compose_create(
            self.atc,
            call_abi_method=args.method(),
            transaction_parameters=_convert_create_transaction_parameters(transaction_parameters, on_complete),
            **_as_dict(args, convert_all=True),
        )
        return self

    def update_bare(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """Adds a calls to the update_application bare method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        self.app_client.compose_update(
            self.atc,
            call_abi_method=False,
            transaction_parameters=_convert_transaction_parameters(transaction_parameters),
        )
        return self

    def delete_bare(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> "Composer":
        """Adds a calls to the delete_application bare method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns Composer: This Composer instance"""

        self.app_client.compose_delete(
            self.atc,
            call_abi_method=False,
            transaction_parameters=_convert_transaction_parameters(transaction_parameters),
        )
        return self

    def clear_state(
        self,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
        app_args: list[bytes] | None = None,
    ) -> "Composer":
        """Adds a call to the application with on completion set to ClearState
    
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :param list[bytes] | None app_args: (optional) Application args to pass"""
    
        self.app_client.compose_clear_state(self.atc, _convert_transaction_parameters(transaction_parameters), app_args)
        return self


class FracticdistributionClient:
    """Fractic Distribution Main Contract
    
    A class for interacting with the fracticdistribution app providing high productivity and
    strongly typed methods to deploy and call the app"""

    @typing.overload
    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        app_id: int = 0,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        creator: str | algokit_utils.Account,
        indexer_client: algosdk.v2client.indexer.IndexerClient | None = None,
        existing_deployments: algokit_utils.AppLookup | None = None,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        ...

    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        creator: str | algokit_utils.Account | None = None,
        indexer_client: algosdk.v2client.indexer.IndexerClient | None = None,
        existing_deployments: algokit_utils.AppLookup | None = None,
        app_id: int = 0,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        """
        FracticdistributionClient can be created with an app_id to interact with an existing application, alternatively
        it can be created with a creator and indexer_client specified to find existing applications by name and creator.
        
        :param AlgodClient algod_client: AlgoSDK algod client
        :param int app_id: The app_id of an existing application, to instead find the application by creator and name
        use the creator and indexer_client parameters
        :param str | Account creator: The address or Account of the app creator to resolve the app_id
        :param IndexerClient indexer_client: AlgoSDK indexer client, only required if deploying or finding app_id by
        creator and app name
        :param AppLookup existing_deployments:
        :param TransactionSigner | Account signer: Account or signer to use to sign transactions, if not specified and
        creator was passed as an Account will use that.
        :param str sender: Address to use as the sender for all transactions, will use the address associated with the
        signer if not specified.
        :param TemplateValueMapping template_values: Values to use for TMPL_* template variables, dictionary keys should
        *NOT* include the TMPL_ prefix
        :param str | None app_name: Name of application to use when deploying, defaults to name defined on the
        Application Specification
            """

        self.app_spec = APP_SPEC
        
        # calling full __init__ signature, so ignoring mypy warning about overloads
        self.app_client = algokit_utils.ApplicationClient(  # type: ignore[call-overload, misc]
            algod_client=algod_client,
            app_spec=self.app_spec,
            app_id=app_id,
            creator=creator,
            indexer_client=indexer_client,
            existing_deployments=existing_deployments,
            signer=signer,
            sender=sender,
            suggested_params=suggested_params,
            template_values=template_values,
            app_name=app_name,
        )

    @property
    def algod_client(self) -> algosdk.v2client.algod.AlgodClient:
        return self.app_client.algod_client

    @property
    def app_id(self) -> int:
        return self.app_client.app_id

    @app_id.setter
    def app_id(self, value: int) -> None:
        self.app_client.app_id = value

    @property
    def app_address(self) -> str:
        return self.app_client.app_address

    @property
    def sender(self) -> str | None:
        return self.app_client.sender

    @sender.setter
    def sender(self, value: str) -> None:
        self.app_client.sender = value

    @property
    def signer(self) -> TransactionSigner | None:
        return self.app_client.signer

    @signer.setter
    def signer(self, value: TransactionSigner) -> None:
        self.app_client.signer = value

    @property
    def suggested_params(self) -> algosdk.transaction.SuggestedParams | None:
        return self.app_client.suggested_params

    @suggested_params.setter
    def suggested_params(self, value: algosdk.transaction.SuggestedParams | None) -> None:
        self.app_client.suggested_params = value

    def get_global_state(self) -> GlobalState:
        """Returns the application's global state wrapped in a strongly typed class with options to format the stored value"""

        state = typing.cast(dict[bytes, bytes | int], self.app_client.get_global_state(raw=True))
        return GlobalState(state)

    def init_fractic_nft_flow(
        self,
        *,
        assert_transfer_txn: TransactionWithSigner,
        time_limit: int,
        max_fraction: int,
        price_per_fraction: int,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[bool]:
        """The entry contract method for Fractic
        It takes an AssetTransferTransaction as a parameter, checks if the contract is opted into the NFT, (implying checks were done previously) then locks the NFT into the contract's account, and creates a pool
        
        Calls `init_fractic_nft_flow(axfer,uint64,uint64,uint64)bool` ABI method
        
        :param TransactionWithSigner assert_transfer_txn: The `assert_transfer_txn` ABI parameter
        :param int time_limit: The `time_limit` ABI parameter
        :param int max_fraction: The `max_fraction` ABI parameter
        :param int price_per_fraction: The `price_per_fraction` ABI parameter
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[bool]: The result of the transaction"""

        args = InitFracticNftFlowArgs(
            assert_transfer_txn=assert_transfer_txn,
            time_limit=time_limit,
            max_fraction=max_fraction,
            price_per_fraction=price_per_fraction,
        )
        result = self.app_client.call(
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return result

    def opt_in_to_asset(
        self,
        *,
        deposit_payment_txn: TransactionWithSigner,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[bool]:
        """An opt-in contract method
        That will make the contract to opt-in to an NFT asset, if the asset is valid for Fractic, which means decimals is 0, and total is 1 provided that the 5 Algo deposit is supplied
        
        Calls `opt_in_to_asset(pay)bool` ABI method
        
        :param TransactionWithSigner deposit_payment_txn: The `deposit_payment_txn` ABI parameter
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[bool]: The result of the transaction"""

        args = OptInToAssetArgs(
            deposit_payment_txn=deposit_payment_txn,
        )
        result = self.app_client.call(
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return result

    def buy_nft_fraction(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[None]:
        """Calls `buy_nft_fraction()void` ABI method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[None]: The result of the transaction"""

        args = BuyNftFractionArgs()
        result = self.app_client.call(
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return result

    def create_create(
        self,
        *,
        dao: str,
        on_complete: typing.Literal["no_op"] = "no_op",
        transaction_parameters: algokit_utils.CreateTransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[None]:
        """Calls `create(address)void` ABI method
        
        :param str dao: The `dao` ABI parameter
        :param typing.Literal[no_op] on_complete: On completion type to use
        :param algokit_utils.CreateTransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[None]: The result of the transaction"""

        args = CreateArgs(
            dao=dao,
        )
        result = self.app_client.create(
            call_abi_method=args.method(),
            transaction_parameters=_convert_create_transaction_parameters(transaction_parameters, on_complete),
            **_as_dict(args, convert_all=True),
        )
        return result

    def update_bare(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.TransactionResponse:
        """Calls the update_application bare method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.TransactionResponse: The result of the transaction"""

        result = self.app_client.update(
            call_abi_method=False,
            transaction_parameters=_convert_transaction_parameters(transaction_parameters),
        )
        return result

    def delete_bare(
        self,
        *,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.TransactionResponse:
        """Calls the delete_application bare method
        
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.TransactionResponse: The result of the transaction"""

        result = self.app_client.delete(
            call_abi_method=False,
            transaction_parameters=_convert_transaction_parameters(transaction_parameters),
        )
        return result

    def clear_state(
        self,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
        app_args: list[bytes] | None = None,
    ) -> algokit_utils.TransactionResponse:
        """Calls the application with on completion set to ClearState
    
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :param list[bytes] | None app_args: (optional) Application args to pass
        :returns algokit_utils.TransactionResponse: The result of the transaction"""
    
        return self.app_client.clear_state(_convert_transaction_parameters(transaction_parameters), app_args)

    def deploy(
        self,
        version: str | None = None,
        *,
        signer: TransactionSigner | None = None,
        sender: str | None = None,
        allow_update: bool | None = None,
        allow_delete: bool | None = None,
        on_update: algokit_utils.OnUpdate = algokit_utils.OnUpdate.Fail,
        on_schema_break: algokit_utils.OnSchemaBreak = algokit_utils.OnSchemaBreak.Fail,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        create_args: DeployCreate[CreateArgs],
        update_args: algokit_utils.DeployCallArgs | None = None,
        delete_args: algokit_utils.DeployCallArgs | None = None,
    ) -> algokit_utils.DeployResponse:
        """Deploy an application and update client to reference it.
        
        Idempotently deploy (create, update/delete if changed) an app against the given name via the given creator
        account, including deploy-time template placeholder substitutions.
        To understand the architecture decisions behind this functionality please see
        <https://github.com/algorandfoundation/algokit-cli/blob/main/docs/architecture-decisions/2023-01-12_smart-contract-deployment.md>
        
        ```{note}
        If there is a breaking state schema change to an existing app (and `on_schema_break` is set to
        'ReplaceApp' the existing app will be deleted and re-created.
        ```
        
        ```{note}
        If there is an update (different TEAL code) to an existing app (and `on_update` is set to 'ReplaceApp')
        the existing app will be deleted and re-created.
        ```
        
        :param str version: version to use when creating or updating app, if None version will be auto incremented
        :param algosdk.atomic_transaction_composer.TransactionSigner signer: signer to use when deploying app
        , if None uses self.signer
        :param str sender: sender address to use when deploying app, if None uses self.sender
        :param bool allow_delete: Used to set the `TMPL_DELETABLE` template variable to conditionally control if an app
        can be deleted
        :param bool allow_update: Used to set the `TMPL_UPDATABLE` template variable to conditionally control if an app
        can be updated
        :param OnUpdate on_update: Determines what action to take if an application update is required
        :param OnSchemaBreak on_schema_break: Determines what action to take if an application schema requirements
        has increased beyond the current allocation
        :param dict[str, int|str|bytes] template_values: Values to use for `TMPL_*` template variables, dictionary keys
        should *NOT* include the TMPL_ prefix
        :param DeployCreate[CreateArgs] create_args: Arguments used when creating an application
        :param algokit_utils.DeployCallArgs | None update_args: Arguments used when updating an application
        :param algokit_utils.DeployCallArgs | None delete_args: Arguments used when deleting an application
        :return DeployResponse: details action taken and relevant transactions
        :raises DeploymentError: If the deployment failed"""

        return self.app_client.deploy(
            version,
            signer=signer,
            sender=sender,
            allow_update=allow_update,
            allow_delete=allow_delete,
            on_update=on_update,
            on_schema_break=on_schema_break,
            template_values=template_values,
            create_args=_convert_deploy_args(create_args),
            update_args=_convert_deploy_args(update_args),
            delete_args=_convert_deploy_args(delete_args),
        )

    def compose(self, atc: AtomicTransactionComposer | None = None) -> Composer:
        return Composer(self.app_client, atc or AtomicTransactionComposer())
