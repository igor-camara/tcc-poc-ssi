from typing import Optional, List, Dict, Any, TypeVar
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, OperationFailure, DuplicateKeyError
from bson import ObjectId
from datetime import datetime
import logging
from modules.config.settings import settings

# Configurar logger
logger = logging.getLogger(__name__)

# TypeVar para permitir genéricos
T = TypeVar('T')


class MongoDBClient:
    """
    Classe abstrata para gerenciar conexões e operações com MongoDB.
    """
    
    def __init__(
        self,
        auth_source: str = "admin"
    ):
        self.host = settings.mongo_host
        self.port = settings.mongo_port
        self.username = settings.mongo_username
        self.password = settings.mongo_password
        self.database_name = settings.mongo_database_name
        self.auth_source = auth_source
        
        self._client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        
    def connect(self) -> None:
        try:
            connection_string = (
                f"mongodb://{self.username}:{self.password}@"
                f"{self.host}:{self.port}/?authSource={self.auth_source}"
            )
            
            self._client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000
            )
            
            # Verifica a conexão
            self._client.admin.command('ping')
            self._db = self._client[self.database_name]
            
            logger.info(f"Conectado ao MongoDB: {self.host}:{self.port}/{self.database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Falha ao conectar ao MongoDB: {e}")
            raise
            
    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            logger.info("Desconectado do MongoDB")
            
    def get_collection(self, collection_name: str) -> Collection:
        if self._db is None:
            raise RuntimeError("Não conectado ao banco de dados. Execute connect() primeiro.")
        return self._db[collection_name]
    
    @property
    def database(self) -> Database:
        if self._db is None:
            raise RuntimeError("Não conectado ao banco de dados. Execute connect() primeiro.")
        return self._db


class MongoDBRepository:
    def __init__(self, client: MongoDBClient, collection_name: str):
        self.client = client
        self.collection_name = collection_name
        
    @property
    def collection(self) -> Collection:
        return self.client.get_collection(self.collection_name)
    
    # ==================== OPERAÇÕES DE INSERÇÃO ====================
    
    def insert_one(self, document: Dict[str, Any]) -> str:
        try:
            # Adiciona timestamp de criação
            if "created_at" not in document:
                document["created_at"] = datetime.utcnow()
                
            result = self.collection.insert_one(document)
            logger.info(f"Documento inserido na coleção '{self.collection_name}': {result.inserted_id}")
            return str(result.inserted_id)
            
        except DuplicateKeyError as e:
            logger.error(f"Chave duplicada ao inserir documento: {e}")
            raise
        except OperationFailure as e:
            logger.error(f"Falha ao inserir documento: {e}")
            raise
    
    def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        try:
            # Adiciona timestamp de criação
            for doc in documents:
                if "created_at" not in doc:
                    doc["created_at"] = datetime.utcnow()
                    
            result = self.collection.insert_many(documents)
            logger.info(f"{len(result.inserted_ids)} documentos inseridos na coleção '{self.collection_name}'")
            return [str(id) for id in result.inserted_ids]
            
        except OperationFailure as e:
            logger.error(f"Falha ao inserir documentos: {e}")
            raise
    
    # ==================== OPERAÇÕES DE CONSULTA ====================
    
    def find_one(
        self,
        filter: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            result = self.collection.find_one(filter, projection)
            if result:
                result["_id"] = str(result["_id"])
            return result
            
        except OperationFailure as e:
            logger.error(f"Erro ao buscar documento: {e}")
            raise
    
    def find_by_id(
        self,
        document_id: str,
        projection: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            return self.find_one({"_id": ObjectId(document_id)}, projection)
        except Exception as e:
            logger.error(f"ID inválido: {document_id} - {e}")
            return None
    
    def find_many(
        self,
        filter: Dict[str, Any] = None,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        try:
            filter = filter or {}
            cursor = self.collection.find(filter, projection)
            
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
                
            results = list(cursor)
            for result in results:
                result["_id"] = str(result["_id"])
                
            return results
            
        except OperationFailure as e:
            logger.error(f"Erro ao buscar documentos: {e}")
            raise
    
    def find_all(
        self,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        return self.find_many(filter={}, projection=projection, sort=sort)
    
    def count(self, filter: Dict[str, Any] = None) -> int:
        filter = filter or {}
        return self.collection.count_documents(filter)
    
    # ==================== OPERAÇÕES DE ATUALIZAÇÃO ====================
    
    def update_one(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        try:
            # Adiciona timestamp de atualização
            if "$set" not in update:
                update["$set"] = {}
            update["$set"]["updated_at"] = datetime.utcnow()
            
            result = self.collection.update_one(filter, update, upsert=upsert)
            
            if result.modified_count > 0 or result.upserted_id:
                logger.info(f"Documento atualizado na coleção '{self.collection_name}'")
                return True
            return False
            
        except OperationFailure as e:
            logger.error(f"Erro ao atualizar documento: {e}")
            raise
    
    def update_by_id(
        self,
        document_id: str,
        update: Dict[str, Any]
    ) -> bool:
        try:
            return self.update_one({"_id": ObjectId(document_id)}, update)
        except Exception as e:
            logger.error(f"Erro ao atualizar documento por ID: {e}")
            return False
    
    def update_many(
        self,
        filter: Dict[str, Any],
        update: Dict[str, Any]
    ) -> int:
        try:
            # Adiciona timestamp de atualização
            if "$set" not in update:
                update["$set"] = {}
            update["$set"]["updated_at"] = datetime.utcnow()
            
            result = self.collection.update_many(filter, update)
            logger.info(f"{result.modified_count} documentos atualizados na coleção '{self.collection_name}'")
            return result.modified_count
            
        except OperationFailure as e:
            logger.error(f"Erro ao atualizar documentos: {e}")
            raise
    
    # ==================== OPERAÇÕES DE EXCLUSÃO ====================
    
    def delete_one(self, filter: Dict[str, Any]) -> bool:
        try:
            result = self.collection.delete_one(filter)
            if result.deleted_count > 0:
                logger.info(f"Documento deletado da coleção '{self.collection_name}'")
                return True
            return False
            
        except OperationFailure as e:
            logger.error(f"Erro ao deletar documento: {e}")
            raise
    
    def delete_by_id(self, document_id: str) -> bool:
        try:
            return self.delete_one({"_id": ObjectId(document_id)})
        except Exception as e:
            logger.error(f"Erro ao deletar documento por ID: {e}")
            return False
    
    def delete_many(self, filter: Dict[str, Any]) -> int:
        try:
            result = self.collection.delete_many(filter)
            logger.info(f"{result.deleted_count} documentos deletados da coleção '{self.collection_name}'")
            return result.deleted_count
            
        except OperationFailure as e:
            logger.error(f"Erro ao deletar documentos: {e}")
            raise
    
    # ==================== OPERAÇÕES AUXILIARES ====================
    
    def exists(self, filter: Dict[str, Any]) -> bool:
        return self.count(filter) > 0
    
    def create_index(self, keys: List[tuple], unique: bool = False) -> str:
        try:
            index_name = self.collection.create_index(keys, unique=unique)
            logger.info(f"Índice '{index_name}' criado na coleção '{self.collection_name}'")
            return index_name
            
        except OperationFailure as e:
            logger.error(f"Erro ao criar índice: {e}")
            raise


# ==================== INSTÂNCIA GLOBAL ====================

_mongodb_client: Optional[MongoDBClient] = None


def get_mongodb_client() -> MongoDBClient:
    global _mongodb_client
    if _mongodb_client is None:
        _mongodb_client = MongoDBClient()
        _mongodb_client.connect()
    return _mongodb_client


def close_mongodb_client() -> None:
    global _mongodb_client
    if _mongodb_client:
        _mongodb_client.disconnect()
        _mongodb_client = None
