import ast
from datetime import datetime
from typing import List, Optional, Set
from bs4 import BeautifulSoup
from database import get_session, get_engine
from ichart.i_chart_meta_data_fetch_service import IChartMetaDataFetchService
from models import InstrumentDetails
import pandas as pd
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert

# Initialize database connections
engine = get_engine()
session = get_session()


def parse_contract_names(html_data: str) -> List[str]:
    """Parse contract names from HTML content.

    Args:
        html_data: HTML string containing contract information

    Returns:
        List of contract names extracted from the HTML
    """
    soup = BeautifulSoup(html_data, 'html.parser')
    contracts = []

    for li in soup.find_all('li', class_='dropdown-item'):
        if 'changeSymbol' in li.get('onclick', ''):
            try:
                contract = li['onclick'].split("'")[1]
                contracts.append(contract)
            except (IndexError, KeyError):
                continue

    return contracts


def create_metadata_service(user_id: str, token: str) -> IChartMetaDataFetchService:
    """Create and return a metadata service instance.

    Args:
        user_id: User ID for authentication
        token: Session token for authentication

    Returns:
        Initialized IChartMetaDataFetchService instance
    """
    return IChartMetaDataFetchService(
        user_id=user_id,
        session_token=token
    )


def get_contract_names(meta_service: IChartMetaDataFetchService,
                       symbol: str, period: str, option_type: str) -> List[str]:
    """Fetch and parse contract names from the metadata service.

    Args:
        meta_service: Initialized metadata service
        symbol: Instrument symbol
        period: Time period ('latest' or 'historical')
        option_type: Option type ('XX' or 'options')

    Returns:
        List of contract names
    """
    html_data = meta_service.process(
        symbol=symbol,
        period=period,
        optionType=option_type
    )
    return parse_contract_names(html_data)


def get_existing_contracts(symbol: str, contracts: List[str]) -> Set[str]:
    """Retrieve existing contracts from the database.

    Args:
        symbol: Instrument symbol to filter by
        contracts: List of contracts to check

    Returns:
        Set of existing contract names
    """
    existing = session.query(InstrumentDetails.instrument_contract).filter(
        InstrumentDetails.instrument_name == symbol,
        InstrumentDetails.instrument_contract.in_(contracts)
    ).all()
    return {c[0] for c in existing}


def save_contract_details(row: pd.Series) -> None:
    """Process and save contract details to the database.

    Args:
        row: Pandas Series containing instrument details
    """
    try:
        contracts_to_process = ast.literal_eval(row['instrument_list'])
    except (ValueError, SyntaxError) as e:
        print(f"Error parsing contracts for {row['symbol']}: {e}")
        return

    existing_contracts = get_existing_contracts(row['symbol'], contracts_to_process)

    for contract in contracts_to_process:
        # Only update historical contracts if they're new
        status = not (row['period'] == 'historical' and contract in existing_contracts)

        stmt = sqlite_upsert(InstrumentDetails).values(
            instrument_name=row['symbol'],
            instrument_contract=contract,
            exchange=row['exchange'],
            segment=row['segment'],
            instrument_type='FUTURE' if row['option_type'] == 'XX' else 'OPTION',
            latest=(row['period'] == 'latest'),
            updated_at=datetime.utcnow()
        ).on_conflict_do_update(
            index_elements=['instrument_contract'],
            set_={
                'latest': status,
                'updated_at': datetime.utcnow()
            }
        )

        session.execute(stmt)

    session.commit()


def generate_instrument_list(meta_service: Optional[IChartMetaDataFetchService] = None) -> None:
    """Main function to generate and save instrument contracts.

    Args:
        meta_service: Optional pre-initialized metadata service
    """
    # Read instruments and create all combinations
    df = pd.read_sql("SELECT * FROM instruments", con=engine)

    periods = ['latest', 'historical']
    option_types = ['XX', 'options']

    # Create all combinations of periods and option types
    df = df.merge(pd.DataFrame({'period': periods}), how='cross')
    df = df.merge(pd.DataFrame({'option_type': option_types}), how='cross')

    # Save current state for debugging
    df.to_csv('savestate.csv', index=False)

    # Process each row
    df.apply(save_contract_details, axis=1)


if __name__ == '__main__':
    user_id = input('your_user_id')
    token = input('your_token')
    meta_service = create_metadata_service(user_id="your_user_id", token="your_token")

    try:
        generate_instrument_list(meta_service)
    except Exception as e:
        print(f"Error in main execution: {e}")
    finally:
        session.close()