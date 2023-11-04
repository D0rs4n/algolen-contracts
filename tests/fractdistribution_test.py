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
from algosdk import transaction
from algosdk.atomic_transaction_composer import TransactionWithSigner
from algosdk.encoding import encode_as_bytes
from algosdk.v2client.algod import AlgodClient
from algosdk.encoding import decode_address
from algosdk.constants import address_len
from smart_contracts.fractdistribution import contract as fractdistribution_contract


@pytest.fixture(scope="session")
def fractdistribution_app_spec(algod_client: AlgodClient) -> ApplicationSpecification:
    return fractdistribution_contract.app.build(algod_client)


@pytest.fixture(scope="session")
def fractdistribution_client(
    algod_client: AlgodClient, fractdistribution_app_spec: ApplicationSpecification
) -> ApplicationClient:
    client = ApplicationClient(
        algod_client,
        app_spec=fractdistribution_app_spec,
        signer=get_localnet_default_account(algod_client),
        template_values={"UPDATABLE": 1, "DELETABLE": 1},
    )
    client.create(
        dao=decode_address(get_localnet_default_account(algod_client).address)
    )
    ensure_funded(
        algod_client,
        EnsureBalanceParameters(
            account_to_fund=client.app_address,
            min_spending_balance_micro_algos=10000000000,
            min_funding_increment_micro_algos=1000000000,
        ),
    )
    return client


@pytest.fixture(scope="function")
def create_valid_nft(
    algod_client: AlgodClient,
    fractdistribution_app_spec: ApplicationSpecification,
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
    fractdistribution_client: ApplicationClient,
    create_valid_nft: int,
) -> None:
    signer = get_localnet_default_account(algod_client)

    params = algod_client.suggested_params()

    unsigned_pmtxn = transaction.PaymentTxn(
        sender=signer.address,
        sp=params,
        receiver=fractdistribution_client.app_address,
        amt=100000,
    )

    assert fractdistribution_client.call(
        "opt_in_to_asset",
        deposit_payment_txn=TransactionWithSigner(unsigned_pmtxn, signer.signer),
        transaction_parameters={
            "boxes": [
                (
                    fractdistribution_client.app_id,
                    (encode_as_bytes("d") + encode_as_bytes(create_valid_nft)),
                ),
            ],
            "foreign_assets": [create_valid_nft],
        },
    ).return_value


@pytest.mark.parametrize("total", [100])
def test_opt_in_nft_with_invalid_params(
    algod_client: AlgodClient,
    fractdistribution_client: ApplicationClient,
    create_valid_nft: int,
) -> None:
    signer = get_localnet_default_account(algod_client)

    params = algod_client.suggested_params()

    unsigned_pmtxn = transaction.PaymentTxn(
        sender=signer.address,
        sp=params,
        receiver=fractdistribution_client.app_address,
        amt=100000,
    )
    with pytest.raises(LogicError):
        fractdistribution_client.call(
            "opt_in_to_asset",
            deposit_payment_txn=TransactionWithSigner(unsigned_pmtxn, signer.signer),
            transaction_parameters={
                "boxes": [
                    (
                        fractdistribution_client.app_id,
                        (encode_as_bytes("d") + encode_as_bytes(create_valid_nft)),
                    ),
                ],
                "foreign_assets": [create_valid_nft],
            },
        )


@pytest.mark.parametrize("total", [1])
def test_init_fractic_nft_flow(
    algod_client: AlgodClient,
    fractdistribution_client: ApplicationClient,
    create_valid_nft: int,
):
    signer = get_localnet_default_account(algod_client)

    params = algod_client.suggested_params()

    unsigned_pmtxn = transaction.PaymentTxn(
        sender=signer.address,
        sp=params,
        receiver=fractdistribution_client.app_address,
        amt=100000,
    )

    fractdistribution_client.call(
        "opt_in_to_asset",
        deposit_payment_txn=TransactionWithSigner(unsigned_pmtxn, signer.signer),
        transaction_parameters={
            "boxes": [
                (
                    fractdistribution_client.app_id,
                    (encode_as_bytes("p") + encode_as_bytes(create_valid_nft)),
                ),
                (
                    fractdistribution_client.app_id,
                    (encode_as_bytes("d") + encode_as_bytes(create_valid_nft)),
                ),
            ],
            "foreign_assets": [create_valid_nft],
        },
    )

    xfer_txn = transaction.AssetTransferTxn(
        sender=signer.address,
        sp=params,
        receiver=fractdistribution_client.app_address,
        amt=1,
        index=create_valid_nft,
    )
    assert fractdistribution_client.call(
        "init_fractic_nft_flow",
        assert_transfer_txn=TransactionWithSigner(xfer_txn, signer.signer),
        time_limit=10000,
        max_fraction=100,
        price_per_fraction=10000000,
        transaction_parameters={
            "boxes": [
                (
                    fractdistribution_client.app_id,
                    (encode_as_bytes("p") + encode_as_bytes(create_valid_nft)),
                ),
                (
                    fractdistribution_client.app_id,
                    (encode_as_bytes("d") + encode_as_bytes(create_valid_nft)),
                ),
            ],
            "foreign_assets": [create_valid_nft],
        },
    ).return_value
