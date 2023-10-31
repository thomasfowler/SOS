"""Context Processors for the Portfolio Planner app."""


def current_path(request):
    """Basic Context Processor to get the current path."""
    return {
        'current_path': request.path
    }