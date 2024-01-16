from rest_framework.permissions import IsAuthenticated

def rest_api_config(
    list=True,
    create=True,
    retrieve=True,
    update=True,
    destroy=True,
    permission=IsAuthenticated
):
    return {
        'list':list,
        'create':create,
        'retrieve':retrieve,
        'update':update,
        'destroy':destroy,
        'permission':permission
    }