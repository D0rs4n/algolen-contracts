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


def test_says_hello(dao_client: ApplicationClient) -> None:
    result = dao_client.call(dao.hello, name="World")

    assert result.return_value == "Hello, World"
