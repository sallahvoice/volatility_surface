from db.repositories.base_repo import BaseRepository
from db.engine import database
from logger import get_logger

logger = get_logger(__file__)


class SnapshotRepo(BaseRepository):
    super().__init__("surface_snapshots", "snapshot_id")

    def create_snapshot(self, symbol, underlying_con_id, spot_price, note=None):
        data = {
            "symbol":symbol,
            "underlying_con_id":underlying_con_id,
            "spot_price":float(spot_price),
            "note":note
        }
        return self.create(data)

    def get_recent(self, symbol, limit=10):
        query=f"""
        SELECT * FROM {self.table}
        WHERE symbol = %s
        ORDER BY captured_at DESC
        LIMIT %s
        """
        with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (symbol, limit))
            return cursor.fetchall()


class DataPointRepo(BaseRepository):
    super().__init__("suface_data_points", "data_point_id")

    def bulk_insertion(self, snapshot_id, data_points):
        if not data_points:
            return 0

        query = """
        INSERT INTO suface_data_points
        (snapshot_id, expiration, strike, implied_vol, option_type)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = [
            (
            snapshot_id,
            dp["expiration"],
            float(dp["strike"]),
            float(dp["implied_vol"]),
            dp["option_type"]
            )
            for dp in data_points
        ]

        with database.get_cursor(dictionary=True) as cursor:
            cursor.executemany(query, values)
            return cursor.rowcount 

    def get_data_for_snapshot(self, snapshot_id):
        query = f"""
        SELECT * FROM {self.table}
        WHERE snapshot_id = %s
        ORDER BY expiration, strike
        """
     with database.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (snapshot_id,))
            return cursor.fetchall() 