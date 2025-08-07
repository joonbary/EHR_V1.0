"""
Base Repository Pattern Implementation
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any
from django.db import models
from django.db.models import QuerySet, Q
from abc import ABC, abstractmethod

ModelType = TypeVar('ModelType', bound=models.Model)


class BaseRepository(Generic[ModelType], ABC):
    """Base repository class for all repositories"""
    
    @property
    @abstractmethod
    def model(self) -> type[ModelType]:
        """Return the model class for this repository"""
        pass
    
    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get a single record by ID"""
        try:
            return self.model.objects.get(pk=id)
        except self.model.DoesNotExist:
            return None
    
    def get_all(self) -> QuerySet[ModelType]:
        """Get all records"""
        return self.model.objects.all()
    
    def filter(self, **kwargs) -> QuerySet[ModelType]:
        """Filter records by given criteria"""
        return self.model.objects.filter(**kwargs)
    
    def create(self, **kwargs) -> ModelType:
        """Create a new record"""
        return self.model.objects.create(**kwargs)
    
    def update(self, instance: ModelType, **kwargs) -> ModelType:
        """Update an existing record"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: ModelType) -> None:
        """Delete a record"""
        instance.delete()
    
    def bulk_create(self, objects: List[ModelType]) -> List[ModelType]:
        """Create multiple records at once"""
        return self.model.objects.bulk_create(objects)
    
    def bulk_update(self, objects: List[ModelType], fields: List[str]) -> None:
        """Update multiple records at once"""
        self.model.objects.bulk_update(objects, fields)
    
    def exists(self, **kwargs) -> bool:
        """Check if records exist with given criteria"""
        return self.model.objects.filter(**kwargs).exists()
    
    def count(self, **kwargs) -> int:
        """Count records with given criteria"""
        return self.model.objects.filter(**kwargs).count()
    
    def get_or_create(self, defaults: Optional[Dict] = None, **kwargs) -> tuple[ModelType, bool]:
        """Get or create a record"""
        return self.model.objects.get_or_create(defaults=defaults, **kwargs)
    
    def update_or_create(self, defaults: Optional[Dict] = None, **kwargs) -> tuple[ModelType, bool]:
        """Update or create a record"""
        return self.model.objects.update_or_create(defaults=defaults, **kwargs)
    
    def search(self, query: str, fields: List[str]) -> QuerySet[ModelType]:
        """Search records in specified fields"""
        q_objects = Q()
        for field in fields:
            q_objects |= Q(**{f"{field}__icontains": query})
        return self.model.objects.filter(q_objects)
    
    def paginate(self, page: int = 1, per_page: int = 10) -> QuerySet[ModelType]:
        """Paginate query results"""
        start = (page - 1) * per_page
        end = start + per_page
        return self.model.objects.all()[start:end]