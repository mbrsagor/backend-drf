class TokenAuthMiddleware:
    """
    Custom middleware to authenticate users via token in query string.
    Example: ws://.../?token=<token_key>
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]

        if token:
            scope["user"] = await get_user(token)
        # Verify if user is not already set by AuthMiddlewareStack (e.g., via session)
        elif "user" not in scope: 
            scope["user"] = AnonymousUser()
        
        return await self.app(scope, receive, send)

