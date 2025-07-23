import pandas as pd
from sqlalchemy import text

from constants import Exchange, Segment
from data import data
from database import get_session
from models import Instruments


def create_instrument(item):
    try:
        return Instruments(
            name=item['name'],
            symbol=item['symbol'],
            exchange=Exchange(item['exchange'].upper()),
            segment=Segment(item['segment'].upper())
        )
    except Exception as e:
        print(f"Invalid item {item.get('symbol', '')}: {e}")
        return None


def seed_instruments_to_db():
    session = get_session()

    try:
        df = pd.DataFrame(data).rename(columns={'underlying': 'name'})
        instruments = df.apply(create_instrument, axis=1).dropna().tolist()
        session.add_all(instruments)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    seed_instruments_to_db()
