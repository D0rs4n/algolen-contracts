import hashlib
import pytest
from algokit_utils import (
    ApplicationClient,
    ApplicationSpecification,
    get_localnet_default_account,
)
from algosdk.v2client.algod import AlgodClient

from algosdk import transaction

from smart_contracts.dao import contract as dao


@pytest.fixture(scope="session")
def dao_app_spec(algod_client: AlgodClient) -> ApplicationSpecification:
    return dao.app.build(algod_client)


@pytest.fixture(scope="session")
def dao_client(
    algod_client: AlgodClient, dao_app_spec: ApplicationSpecification
) -> ApplicationClient:
    client = ApplicationClient(
        algod_client,
        app_spec=dao_app_spec,
        signer=get_localnet_default_account(algod_client),
        template_values={"UPDATABLE": 1, "DELETABLE": 1},
    )
    client.create()
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


def test_gov_opt_in(dao_client: ApplicationClient) -> None:
    assert dao_client.call(dao.gov_opt_in).return_value


def test_says_hello(dao_client: ApplicationClient) -> None:
    result = dao_client.call(dao.hello, name="World")

    assert result.return_value == "Hello, World"
