from algokit_utils import get_algonode_config, get_algod_client
import algosdk.mnemonic as mnemonic
from smart_contracts.algolen.contract import app
from algosdk.atomic_transaction_composer import TransactionWithSigner, AccountTransactionSigner
from algokit_utils import (
    ApplicationClient
)
from algosdk import transaction
from algosdk.encoding import encode_as_bytes

algonode_config = get_algonode_config("testnet", "algod", "")
algod_client = get_algod_client(algonode_config)
mnemonic_s = "shift fiber lumber glass cup sketch dwarf draft dry high iron web can ancient ivory stamp version almost truth nephew fox gain cave above thought"
privkey = mnemonic.to_private_key(mnemonic=mnemonic_s)

algolen_app_spec = app.build(algod_client)

class fuckyou:
    def __init__(self, privkey, address) -> None:
        self.private_key = privkey
        self.address = address

signer = fuckyou(privkey, "QI3VWZGXEMSGLXTL7BINRGKHD4VAWACEJRO343LZ2XU2OZZPNODXKB5DNE")
client = ApplicationClient(
        algod_client,
        app_spec=algolen_app_spec,
        signer=signer,
        app_id=478327734
)
params = algod_client.suggested_params()
"""
unsigned_pmtxn = transaction.PaymentTxn(
        sender=signer.address,
        sp=params,
        receiver=client.app_address,
        amt=1_000_000,
    )

client.call(
        "opt_in_to_asset",
        deposit_payment_txn=TransactionWithSigner(unsigned_pmtxn, AccountTransactionSigner(privkey)),
        transaction_parameters={
            "foreign_assets": [468408812],
        },
    )
"""
xfer_txn = transaction.AssetTransferTxn(
        sender=signer.address,
        sp=params,
        receiver=client.app_address,
        amt=1,
        index=468408812,
)
client.call(
        "list_nft",
        asset_transfer_txn=TransactionWithSigner(xfer_txn, AccountTransactionSigner(privkey)),
        deposit=10_000_000,
        price_per_day=1_000_000,
        max_duration_in_days=2,
        transaction_parameters={
            "boxes": [
                (
                    client.app_id,
                    encode_as_bytes(468408812),
                ),
            ],
            "foreign_assets": [468408812],
        },
)
