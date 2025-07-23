import json
from datetime import datetime
from typing import Tuple, Optional

import pandas as pd
import requests
from sqlalchemy import text, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database import get_engine, get_session
from ichart.ichart_url import IChartURL
from models import InstrumentDetails, MinOHLCV


# ========================
# DATA VALIDATION & FORMATTING
# ========================

def validate_ohlcv_data(ohlcv_data: dict) -> Tuple[bool, str]:
    """Validate OHLCV data structure and status"""
    if ohlcv_data.get('s') != 'ok':
        return False, "Data status is not 'ok'"
    if not all(key in ohlcv_data for key in ['t', 'o', 'h', 'l', 'c', 'v']):
        return False, "Missing required OHLCV fields"
    if not all(len(ohlcv_data[key]) == len(ohlcv_data['t']) for key in ['o', 'h', 'l', 'c', 'v']):
        return False, "Mismatched data lengths"
    return True, ""


def create_ohlcv_dataframe(instrument_id: int, ohlcv_data: dict) -> Optional[pd.DataFrame]:
    """Create properly formatted DataFrame from OHLCV data"""
    try:
        return pd.DataFrame({
            'instrument_id': instrument_id,
            'timestamp': ohlcv_data['t'],
            'open': ohlcv_data['o'],
            'high': ohlcv_data['h'],
            'low': ohlcv_data['l'],
            'close': ohlcv_data['c'],
            'volume': ohlcv_data['v']
        })
    except Exception as e:
        print(f"Error creating DataFrame: {e}")
        return None


# ========================
# DATABASE OPERATIONS
# ========================

def generic_upsert(engine, df: pd.DataFrame) -> Tuple[int, str]:
    """Database-agnostic upsert fallback"""
    inserted_count = 0
    error_messages = []

    with engine.begin() as conn:
        for _, row in df.iterrows():
            try:
                conn.execute(
                    text("""
                    INSERT INTO min_ohlcv
                    (instrument_id, timestamp, open, high, low, close, volume)
                    VALUES (:instrument_id, :timestamp, :open, :high, :low, :close, :volume)
                    ON CONFLICT (instrument_id, timestamp) DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume,
                        updated_at = EXCLUDED.updated_at
                    """),
                    row.to_dict()
                )
                inserted_count += 1
            except IntegrityError:
                continue  # Skip duplicate rows
            except Exception as e:
                error_messages.append(str(e))

    return inserted_count, "; ".join(error_messages) if error_messages else ""


def insert_min_ohlcv_dataframe(engine, instrument_id: int, ohlcv_data: dict) -> Tuple[bool, int, str]:
    """
    Insert OHLCV data with proper error handling and upsert capability

    Returns:
        Tuple: (success: bool, inserted_count: int, error_message: str)
    """
    # Validate input
    is_valid, validation_msg = validate_ohlcv_data(ohlcv_data)
    if not is_valid:
        return False, 0, validation_msg

    # Create DataFrame
    df = create_ohlcv_dataframe(instrument_id, ohlcv_data)
    if df is None or df.empty:
        return True, 0, "No data to insert"

    # Attempt insertion
    inserted_count = 0
    error_msg = ""

    try:
        inserted_count = df.to_sql(
            name='min_ohlcv',
            con=engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )
    except IntegrityError:
        # Fallback to row-by-row upsert if bulk insert fails
        inserted_count, error_msg = generic_upsert(engine, df)
    except SQLAlchemyError as e:
        error_msg = f"Database error: {str(e)}"
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"

    if error_msg:
        print(f"Completed with {inserted_count} inserts. Errors: {error_msg}")
        return (inserted_count > 0), inserted_count, error_msg

    print(f"Successfully inserted/updated {inserted_count} records")
    return True, inserted_count, ""


# ========================
# API COMMUNICATION
# ========================

def _get_headers(session_token: str) -> dict:
    """Generate request headers with session token"""
    return {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'Cookie': f'PHPSESSID={session_token}; _ga=GA1.1.1975893623.1751876892; _fbp=fb.1.1751876892861.4211340581522152; _ga_ZN58C89YGF=GS2.1.s1752080392$o5$g1$t1752080830$j21$l0$h0; PHPSESSID=mck1bkb0pb3lc0gvhljp7goevg'
    }

def generate_url(user_name, session_token, instrument_contract: str) -> str:
    base_url = f'{IChartURL.BASE_URL}/{IChartURL.DATA_URL}'
    params = {
        'symbol': instrument_contract,
        'resolution': '1',
        'from': '1999-07-09',
        'to': datetime.now().strftime('%Y-%m-%d'),
        'u': user_name,
        'sid': session_token,
        'DataRequest': '2',
        'firstDataRequest': 'true'
    }
    return f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"


def update_prices(user_name, session_token: str) -> None:
    """Main function to update prices for all instruments"""
    engine = get_engine()
    session = get_session()

    # session.query(text('delete from min_ohlcv'))
    headers = _get_headers(session_token)

    try:
        for instrument in session.query(InstrumentDetails).all():
            try:
                response = requests.get(
                    generate_url(user_name,
                                 session_token,
                                 instrument.instrument_contract),
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                print(generate_url(user_name, session_token, instrument.instrument_contract))
                print(response.text)
                result = insert_min_ohlcv_dataframe(
                    engine,
                    instrument.id,
                    json.loads(response.text))

                if not result[0]:
                    print(f"Failed to update {instrument.instrument_contract}: {result[2]}")

            except requests.RequestException as e:
                print(f"API request failed for {instrument.instrument_contract}: {e}")
            except json.JSONDecodeError as e:
                print(f"Invalid JSON response for {instrument.instrument_contract}: {e}")

    finally:
        session.close()


if __name__ == '__main__':
    # user_id = input('your_user_id')
    # token = input('your_token')

    user_id = 'Mitesh.Patel'
    token = '3fb87c0p50t42h3qtm7885jcr1'
    update_prices(user_id, token)
