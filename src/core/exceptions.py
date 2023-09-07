from fastapi import HTTPException, status

from core.config import settings

not_valid_credentials_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Could not validate credentials",
)

not_enough_permission_exception = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Not enough permissions",
)

user_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found",
)

user_not_authorized_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authorized")

ticket_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Ticket not found",
)

user_already_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="User with such email exists",
)

quarter_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Quarter not found",
)

review_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Review not found",
)

question_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Question not found",
)

template_not_found_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Template not found",
)

questions_is_not_part_of_this_review = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Questions is not a part of this review",
)

evaluated_user_cant_be_reviewer = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Evaluated user can't be reviewer",
)

review_already_sent_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Review already sent",
)

not_all_questions_answered = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Not all questions is answered",
)

not_available_image_type_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail=f"The file must have one of the following types: {', '.join(settings().available_avatar_types)}",
)

quarter_already_exists_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Quarter with this period already exists",
)

upload_avatar_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Error uploading avatar",
)

delete_avatar_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Error deleting avatar",
)

oauth_bad_response = HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

oauth_data_missed_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail="Readable data is missed. Processing not allowed"
)

oauth_ticket_not_found_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="OAuth ticket not found"
)
