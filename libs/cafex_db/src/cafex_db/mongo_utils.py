from cafex_core.logging.logger_ import CoreLogger
from cafex_db.db_security import DBSecurity


class MongoDBUtils:

    def __init__(
        self, pstr_username=None, pstr_password=None, pstr_cluster_url=None, pstr_database_name=None
    ):
        """Initializes the MongoDBUtils class."""
        self.__obj_db_decrytor = DBSecurity()
        self.logger = CoreLogger(name=__name__).get_logger()
        self.client = self.__mongo_connect(
            pstr_username, pstr_password, pstr_cluster_url, pstr_database_name
        )

    def __mongo_connect(self, pstr_username, pstr_password, pstr_cluster_url, pstr_database_name):
        """Establishes a connection to a MongoDB database.

        Parameters:
        pstr_username (str): The username for MongoDB authentication.
        pstr_password (str): The pwd for MongoDB authentication.
        pstr_cluster_url (str): The MongoDB cluster URL.
        pstr_database_name (str): The name of the database to connect to.

        Returns:
        MongoClient: A MongoClient instance connected to the specified database.

        Raises:
        Exception: If an error occurs during the connection process.
        """
        try:
            self.client = self.__obj_db_decrytor.establish_mongodb_connection(
                pstr_username, pstr_password, pstr_cluster_url, pstr_database_name
            )
            if self.client:
                self.client.admin.command("ping")
                self.logger.info("MongoDB connection established successfully.")
                return self.client
        except Exception as e:
            self.logger.exception("Error occurred in mongo_connect: " + str(e))
            raise Exception(e)

    def mongo_execute(self, database_name, collection_name):
        """Executes a query to retrieve documents from a specified collection
        in a MongoDB database.

        Parameters:
        database_name (str): The name of the database to query.
        collection_name (str): The name of the collection (table) to query.

        Returns:
        dict: The first document retrieved from the collection.

        Raises:
        Exception: If an error occurs during the query execution.
        """
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            for document in collection.find():
                return document
        except Exception as e:
            self.client.close()
            self.logger.exception("Error occurred in mongo_execute: " + str(e))
            raise Exception(e)

    def mongo_execute_parameters(self, database_name, collection_name, projection, query=None):
        """Executes a query to retrieve documents from a specified collection
        in a MongoDB database with a given projection.

        Parameters:
        database_name (str): The name of the database to query.
        collection_name (str): The name of the collection (table) to query.
        projection (dict): The fields to include or exclude in the returned documents.
        query (dict): The query to filter the documents.

        Returns:
        list: The documents retrieved from the collection.

        Raises:
        Exception: If an error occurs during the query execution.
        """
        try:
            result = []
            db = self.client[database_name]
            collection = db[collection_name]
            if query is None:
                query = {}
            documents = collection.find(query, projection)
            for document in documents:
                result.append(document)
            return result
        except Exception as e:
            self.client.close()
            self.logger.exception("Error occurred in mongo_execute_parameters: " + str(e))
            raise Exception(e)

    def get_mongo_records_based_on_aggregate_query(
        self, pstr_database_name, pstr_collection_name, aggregate_query, allowDiskUse=False
    ):
        """Retrieves the list of records from a MongoDB view based on an
        aggregate query.

        Parameters:
        pstr_database_name (str): The name of the database to query.
        pstr_collection_name (str): The name of the collection (table) to query.
        aggregate_query (dict): The aggregate query to filter the documents.
        allowDiskUse (bool): The flag to allow disk use for the query.By default, it is False.

        Returns:
        list: The list of documents retrieved from the collection.
        """
        try:
            db = self.client[pstr_database_name]
            collection = db[pstr_collection_name]
            if not allowDiskUse:
                record_list = list(collection.aggregate(aggregate_query))
            else:
                record_list = list(collection.aggregate(aggregate_query, allowDiskUse=allowDiskUse))
            return record_list
        except Exception as e:
            self.client.close()
            self.logger.exception(
                f"Error occurred in get_mongo_records_based_on_aggregate_query: {e}"
            )
            raise Exception(e)

    def get_collection_count(self, database_name, collection_name):
        """Retrieves the count of documents in a specified collection in a
        MongoDB database.

        Parameters:
        database_name (str): The name of the database to query.
        collection_name (str): The name of the collection (table) to query.

        Returns:
        int: The count of documents in the specified collection.

        Raises:
        Exception: If an error occurs during the query execution.
        """
        try:
            db = self.client[database_name]
            count = db[collection_name].count_documents({})
            return count
        except Exception as e:
            self.client.close()
            self.logger.exception("Error occurred in get_collection_count: " + str(e))
            raise Exception(e)

    def get_specific_document_from_collection(self, database_name, collection_name, query):
        """Retrieves a specific document from a collection in a MongoDB
        database.

        Parameters:
        database_name (str): The name of the database to query.
        collection_name (str): The name of the collection (table) to query.
        query (dict): The query to filter the documents.

        Returns:
        dict: The document that matches the query.

        Raises:
        Exception: If an error occurs during the query execution.
        """
        try:
            db = self.client[database_name]
            document = db[collection_name].find_one(query)
            return document
        except Exception as e:
            self.client.close()
            self.logger.exception(
                "Error occurred in get_specific_document_from_collection: " + str(e)
            )
            raise Exception(e)

    def close_connection(self):
        """Closes the connection to the MongoDB database.

        Returns:
        None
        """
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            self.logger.exception("Error occurred in close_connection: " + str(e))
            raise Exception(e)
