import hashlib

import pytest
from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_localnet_default_account,
    LogicError,
    ensure_funded,
    EnsureBalanceParameters,
)
from algosdk.v2client.algod import AlgodClient
from algosdk import transaction
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algosdk.encoding import encode_as_bytes
from smart_contracts.algolen.contract import app
import algosdk


@pytest.fixture(scope="session")
def algolen_app_spec(algod_client: AlgodClient) -> ApplicationSpecification:
    return app.build(algod_client)


@pytest.fixture(scope="session")
def algolen(
    algod_client: AlgodClient, algolen_app_spec: ApplicationSpecification
) -> ApplicationClient:
    client = ApplicationClient(
        algod_client,
        app_spec=algolen_app_spec,
        signer=get_localnet_default_account(algod_client),
        template_values={"UPDATABLE": 1, "DELETABLE": 1},
    )
    client.create()
    ensure_funded(
        algod_client,
        EnsureBalanceParameters(
            account_to_fund=client.app_address,
            min_spending_balance_micro_algos=1_000_000,
            min_funding_increment_micro_algos=1_000_000,
        ),
    )
    return client


@pytest.fixture(scope="function")
def create_valid_nft(
    algod_client: AlgodClient,
    algolen_app_spec: ApplicationSpecification,
    total: int,
) -> int:
    # Get the default signer for localnet
    signer = get_localnet_default_account(algod_client)
    sp = algod_client.suggested_params()

    metadata = {"data": "data"}

    metadata_hash = hashlib.sha256(str(metadata).encode()).digest()

    # Construct an NFT that satisfies Fractic criteria
    txn = transaction.AssetConfigTxn(
        sender=signer.address,
        sp=sp,
        default_frozen=False,
        unit_name="TEST",
        asset_name="Test NFT",
        manager=signer.address,
        reserve=signer.address,
        freeze=signer.address,
        clawback=signer.address,
        url="random.url",
        metadata_hash=metadata_hash,
        total=total,
        decimals=0,
    )
    # Sign the Asset Creation Transaction and submit it to Localnet, then wait for confirmation
    stxn = txn.sign(signer.private_key)
    txid = algod_client.send_transaction(stxn)
    results = transaction.wait_for_confirmation(algod_client, txid, 4)

    return int(results["asset-index"])


@pytest.mark.parametrize("total", [1])
def test_opt_in_nft_valid_nft(
    algod_client: AlgodClient,
    algolen: ApplicationClient,
    create_valid_nft: int,
) -> None:
    signer = get_localnet_default_account(algod_client)

    params = algod_client.suggested_params()

    unsigned_pmtxn = transaction.PaymentTxn(
        sender=signer.address,
        sp=params,
        receiver=algolen.app_address,
        amt=1_000_000,
    )

    assert algolen.call(
        "opt_in_to_asset",
        deposit_payment_txn=TransactionWithSigner(unsigned_pmtxn, signer.signer),
        transaction_parameters={
            "foreign_assets": [create_valid_nft],
        },
    ).return_value


@pytest.mark.parametrize("total", [100])
def test_opt_in_nft_with_invalid_params(
    algod_client: AlgodClient,
    algolen: ApplicationClient,
    create_valid_nft: int,
) -> None:
    signer = get_localnet_default_account(algod_client)

    params = algod_client.suggested_params()

    unsigned_pmtxn = transaction.PaymentTxn(
        sender=signer.address,
        sp=params,
        receiver=algolen.app_address,
        amt=100000,
    )
    with pytest.raises(LogicError):
        algolen.call(
            "opt_in_to_asset",
            deposit_payment_txn=TransactionWithSigner(unsigned_pmtxn, signer.signer),
            transaction_parameters={
                "foreign_assets": [create_valid_nft],
            },
        )


@pytest.mark.parametrize("total", [1])
def test_list_delist_nft(
    algod_client: AlgodClient,
    algolen: ApplicationClient,
    create_valid_nft: int,
):
    signer = get_localnet_default_account(algod_client)

    params = algod_client.suggested_params()

    unsigned_pmtxn = transaction.PaymentTxn(
        sender=signer.address,
        sp=params,
        receiver=algolen.app_address,
        amt=1_000_000,
    )

    algolen.call(
        "opt_in_to_asset",
        deposit_payment_txn=TransactionWithSigner(unsigned_pmtxn, signer.signer),
        transaction_parameters={
            "foreign_assets": [create_valid_nft],
        },
    )

    balance_before = algod_client.account_info(algolen.app_address)["amount"]

    xfer_txn = transaction.AssetTransferTxn(
        sender=signer.address,
        sp=params,
        receiver=algolen.app_address,
        amt=1,
        index=create_valid_nft,
    )
    assert algolen.call(
        "list_nft",
        assert_transfer_txn=TransactionWithSigner(xfer_txn, signer.signer),
        deposit=10_000_000,
        price_per_day=1_000_000,
        max_duration_in_days=2,
        transaction_parameters={
            "boxes": [
                (
                    algolen.app_id,
                    encode_as_bytes(create_valid_nft),
                ),
            ],
            "foreign_assets": [create_valid_nft],
        },
    ).return_value

    unsigned_pmtxn = transaction.PaymentTxn(
        sender=signer.address,
        sp=params,
        receiver=algolen.app_address,
        amt=1_000,
    )

    assert algolen.call(
        "delist_nft",
        fee_payment_txn=TransactionWithSigner(unsigned_pmtxn, signer.signer),
        asset_id=create_valid_nft,
        transaction_parameters={
            "boxes": [
                (
                    algolen.app_id,
                    encode_as_bytes(create_valid_nft),
                ),
            ],
            "foreign_assets": [create_valid_nft],
        },
    ).return_value

    balance_after = algod_client.account_info(algolen.app_address)["amount"]

    assert balance_before == balance_after
