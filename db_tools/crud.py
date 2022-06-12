import pymysql


class DbClient(pymysql.Connection):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_randomly_ordered_users(self):
        with self.cursor() as cursor:
            cursor.execute("SELECT * FROM players ORDER BY RAND()")

    def get_users_mal_account(self, discord_id: int):
        with self.cursor() as cursor:
            cursor.execute("SELECT mal_id FROM mal_info WHERE discord_id = %s", (discord_id))
            return cursor.fetchone()[0]

    def connect_users_mal_account(self, mal_name: str, discord_id: int, autocommit: bool = True):
        with self.cursor() as cursor:
            cursor.execute("INSERT INTO mal_info VALUES (%s, %s)", (discord_id, mal_name))
        if autocommit:
            self.commit()
        return

    def create_user(self, discord_id: int, address: str, phone: int | None = None, autocommit: bool = True):
        with self.cursor() as cursor:
            cursor.execute("INSERT INTO players(discord_id, address) VALUES (%s, %s)", (discord_id, address))
            if phone:
                cursor.execute("UPDATE players SET phone=%s WHERE discord_id=%s", (phone, discord_id))
        if autocommit:
            self.commit()
        return
