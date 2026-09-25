from .mocks import mock_score as score_service
from .recommendation_service import recommend_standard
from .search_service import search_standards

recommendation_service = recommend_standard

__all__ = [
    "recommendation_service",
    "score_service",
    "search_standards",
]