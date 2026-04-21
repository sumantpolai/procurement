from fastapi import HTTPException, status


class PRNotFoundException(HTTPException):
    def __init__(self, pr_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "PR_NOT_FOUND",
                "message": f"Purchase Request with id {pr_id} not found"
            }
        )


class ItemNotFoundException(HTTPException):
    def __init__(self, item_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "ITEM_NOT_FOUND",
                "message": f"Item with id {item_id} not found in Item Master"
            }
        )


class InvalidStatusTransitionException(HTTPException):
    def __init__(self, current_status: str, new_status: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_STATUS_TRANSITION",
                "message": f"Cannot transition from {current_status} to {new_status}"
            }
        )


class DatabaseException(HTTPException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "DATABASE_ERROR",
                "message": message
            }
        )
