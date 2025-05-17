import sqlite3

class Database:
    def __init__(self, db_name):
        # Connect to the Database
        self.connection = sqlite3.connect(db_name, check_same_thread=False)

    def execute_query(self, query, params=None):
        """ Execute Specified query """
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchone()


class SQLGenerator:
    def __init__(self):
        pass
    
    def generate_query(self, intent, gym_name, time, weekend_info):
        """
        Generates query based on the intent and details
        For now our only trained intent is to view capacity of a gym
        """
        # Initialize List to store Specific Conditions
        conditions = []

        # If Intent is to Get Gym Details
        if intent == 0:
            query = "SELECT AVG(capacity) FROM gym_capacity_summary"

            # Add Conditions based on User Input
            if gym_name:
                conditions.append(f"gym_name = ?")
            if time:
                conditions.append(f"time = ?")
            if weekend_info is not None:
                conditions.append(f"is_weekend = ?")

            # Add Conditions into SQL Query
            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        elif intent in [1, 2]:
            query = "SELECT gym_name, AVG(capacity) AS avg_capacity FROM gym_capacity_summary"

             # Add Conditions based on User Input
            if time:
                conditions.append(f"time = ?")
            if weekend_info is not None:
                conditions.append(f"is_weekend = ?")

            # Add Conditions into SQL Query
            if conditions:
                query += " WHERE " + " AND ".join(conditions) + " GROUP BY gym_name"

            # Order by Asc/Desc depending on Intent 1 or 2
            if intent == 1:         
                query += " ORDER BY avg_capacity ASC LIMIT 1"
            else:
                query += " ORDER BY avg_capacity DESC LIMIT 1"

        elif intent == 3:
            query = "SELECT time, AVG(capacity) as avg_capacity FROM gym_capacity_summary"

             # Add Conditions based on User Input
            if gym_name:
                conditions.append(f"gym_name = ?")
            if weekend_info is not None:
                conditions.append(f"is_weekend = ?")

            # Add Conditions into SQL Query
            if conditions:
                query += " WHERE " + " AND ".join(conditions) + " GROUP BY time ORDER BY avg_capacity ASC LIMIT 1"

        return query