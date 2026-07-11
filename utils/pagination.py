from flask import request


def get_pagination(default_limit=10, max_limit=100):
    """Parse safe pagination parameters from query string."""
    limit = request.args.get("limit", default=default_limit, type=int)
    offset = request.args.get("offset", default=0, type=int)

    if limit is None or limit <= 0:
        limit = default_limit
    if limit > max_limit:
        limit = max_limit
    if offset is None or offset < 0:
        offset = 0

    return limit, offset
