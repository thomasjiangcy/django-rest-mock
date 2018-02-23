from rest_framework import generics, views
from rest_framework.response import Response


class SomeView(views.APIView):
    """
    URL: /api/someview
    """

    def get(self, request, *args, **kwargs):
        """
        ```
        {
            "success": "Hello, world!"
        }
        ```
        """
        pass


class ResourceListView(generics.ListCreateAPIView):
    """
    URL: /api/resource/__key
    """

    def post(self, request, *args, **kwargs):
        """
        ```
        {
            "__options": {
                    "excludeKey": true
            }
        }
        ```
        """
        pass


class ResourceView(generics.RetrieveUpdateDestroyAPIView):
    """
    URL: /api/resource/__key
    """

    def get(self, request, *args, **kwargs):
        """
        ```
        {
            "__key": "<id:int>",
            "__key_position": "url",
            "__mockcount": 5,
            "__options": {
                "modifiers": ["patch", "put", "delete"],
                "excludeKey": false
            },
            "id": "<int>",
            "name": "<name>",
            "complexStructure": [
                {
                    "link": "<int::10>",
                    "url": "<uri>",
                    "related_user": {
                        "id": "<int:1:5>",
                        "hash": "<sha256>"
                    }
                }
            ]
	    }
        ```
        """
        return Response({'success': 'Successful request and response!'}, status=200)
    
    def patch(self, request, *args, **kwargs):
        """Some docstring"""
        pass
    
    def put(self, request, *args, **kwargs):
        """some docstring"""
        pass
    
    def delete(self, request, *args, **kwargs):
        """Some docstring"""
        pass
