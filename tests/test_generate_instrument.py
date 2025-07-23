from unittest.mock import patch, MagicMock

import pandas as pd
import pytest
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

from constants import Exchange, Segment
from data_migration_script.generate_instrument import create_instrument, seed_instruments_to_db
from data_migration_script.ichart.generate_instrument_list import parse_contract_names, create_metadata_service, \
    get_contract_names
from ichart.i_chart_meta_data_fetch_service import IChartMetaDataFetchService

# Test data
TEST_DATA = [
    {"name": "NIFTY", "symbol": "NIFTY", "exchange": "NSE", "segment": "INDEX"},
    {"name": "BANKNIFTY", "symbol": "BANKNIFTY", "exchange": "NSE", "segment": "INDEX"},
    # Add more test cases as needed
]

INVALID_DATA = [
    {"name": "TEST", "symbol": "TEST", "exchange": "INVALID", "segment": "INDEX"},  # Invalid exchange
    {"name": "TEST", "symbol": "TEST", "exchange": "NSE", "segment": "INVALID"},  # Invalid segment
    {"name": "", "symbol": "", "exchange": "", "segment": ""},  # Empty values
    {},  # Empty dict
]

fake = Faker()


@pytest.fixture
def mock_session():
    with patch('database.get_session') as mock:
        session = MagicMock()
        mock.return_value = session
        yield session


def test_create_instrument_valid():
    """Test creating instrument with valid data"""
    item = TEST_DATA[0]
    instrument = create_instrument(item)

    assert instrument is not None
    assert instrument.name == item['name']
    assert instrument.symbol == item['symbol']
    assert instrument.exchange == Exchange[item['exchange'].upper()]
    assert instrument.segment == Segment[item['segment'].upper()]


@pytest.mark.parametrize("item", INVALID_DATA)
def test_create_instrument_invalid(item):
    """Test creating instrument with invalid data"""
    instrument = create_instrument(item)
    assert instrument is None









def test_parse_contract_names():
    soup = """<li class="dropdown-item symbolLiList" style="list-style-type:none;" onclick="changeSymbol('SENSEX25JUL29')">SENSEX 25JUL29 </li>
            <li class="dropdown-item symbolLiList" style="list-style-type:none;" onclick="changeSymbol('BANKEX25JUL29')">BANKEX 25JUL29 </li>
            <li class="dropdown-item symbolLiList" style="list-style-type:none;" onclick="changeSymbol('GODREJCP25JUL31')">GODREJCP 25JUL31 </li>
            <li class="dropdown-item symbolLiList" style="list-style-type:none;" onclick="changeSymbol('CONCOR25JUL31')">CONCOR 25JUL31 </li>"""
    data = parse_contract_names(soup)

    test_data = ['SENSEX25JUL29', 'BANKEX25JUL29', 'GODREJCP25JUL31', 'CONCOR25JUL31']

    data.sort()
    test_data.sort()

    assert set(data) - set(test_data) == set()
    assert 'SENSEX25JUL29' in data
    assert 'priya' not in data


def test_create_metadata_service():
    test_user_id = fake.unique.word().upper()
    test_token = fake.unique.word().upper()
    ob = create_metadata_service(test_user_id, test_token)
    assert isinstance(ob, IChartMetaDataFetchService)
    assert ob.user_id == test_user_id
    assert ob.session_token == test_token


def test_get_contract_names():
    test_user_id = fake.unique.word().upper()
    test_token = fake.unique.word().upper()
    ob = create_metadata_service(test_user_id, test_token)
    response = None
    with patch('requests.request') as mock_request:
        # Setup mock response
        mock_response = MagicMock()
        mock_response.text = """<li class="dropdown-item symbolLiList" style="list-style-type:none;" onclick="changeSymbol('SENSEX25JUL29')">SENSEX 25JUL29 </li>
            <li class="dropdown-item symbolLiList" style="list-style-type:none;" onclick="changeSymbol('BANKEX25JUL29')">BANKEX 25JUL29 </li>
            <li class="dropdown-item symbolLiList" style="list-style-type:none;" onclick="changeSymbol('GODREJCP25JUL31')">GODREJCP 25JUL31 </li>
            <li class="dropdown-item symbolLiList" style="list-style-type:none;" onclick="changeSymbol('CONCOR25JUL31')">CONCOR 25JUL31 </li>"""
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        response = get_contract_names(ob, 'NIFTY', 'latest', 'XX')

    assert type(response) == type([])

    test_data = ['SENSEX25JUL29', 'BANKEX25JUL29', 'GODREJCP25JUL31', 'CONCOR25JUL31']

    response.sort()
    test_data.sort()

    assert set(response) - set(test_data) == set()
    assert 'SENSEX25JUL29' in response
