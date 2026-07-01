from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.orm import aliased, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from db_tables.tables import CommentTable, LikeTable, PostTable
from utils.APIResponce_error_code_enum import SYSTEM_ERROR_CODES, USER_ERROR_CODES
from utils.logging.helper_log import LogState, log_state
from utils.logging.logEvents import PostingLogs
from utils.schemas import APIResponse, CommentCreateSchema, PostCreateSchema


async def get_Nposts_service(user_payload, db: AsyncSession, limit: int = 10, offset: int = 0, search: Optional[str] = None, personal_only: bool = False) -> APIResponse:
    log_state(PostingLogs.POSTING_SERVICE_STARTED, function="get_Nposts_service", user_id=user_payload.user_id, level=LogState.INFO)

    try:
        log_state(PostingLogs.VALIDATING_REQUEST, function="get_Nposts_service", user_id=user_payload.user_id, level=LogState.INFO)

        if limit <= 0:
            log_state(PostingLogs.OPERATION_FAILED, function="get_Nposts_service", user_id=user_payload.user_id, level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNSUPPORTED_INPUT.value,
                error_message="Limit must be greater than zero."
            )

        current_user = user_payload.model_dump()
        post_alias = aliased(PostTable, name="post")

        log_state(PostingLogs.FETCHING_POSTS, function="get_Nposts_service", user_id=current_user["user_id"], level=LogState.INFO)

        stmt = (
            select(
                post_alias,
                func.count(LikeTable.post_id).label("likes")
            )
            .join(
                LikeTable,
                LikeTable.post_id == post_alias.post_id,
                isouter=True
            )
            .group_by(post_alias.post_id)
        )

        #if he is on his own profile or main page (ill extract this data form js)
        if personal_only:
            stmt = stmt.where(
                post_alias.user_id == current_user["user_id"]
            )
        else:
            stmt = stmt.where(
                post_alias.user_id != current_user["user_id"],
                post_alias.published.is_(True)
            )


        if search:
            stmt = stmt.where(
                post_alias.title.contains(search)
            )

        stmt = stmt.offset(offset).limit(limit)

        log_state(
            PostingLogs.EXECUTING_DATABASE_QUERY, function="get_Nposts_service", user_id=current_user["user_id"], level=LogState.INFO)

        result = await db.execute(stmt)
        results = result.all()


        log_state(PostingLogs.SUCCESS, function="get_Nposts_service", user_id=current_user["user_id"], level=LogState.INFO)
        
        return APIResponse(
            success=True,
            data=results,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e: #i couldve called custom exceptions dw, ill see if others require them ill change here

        log_state(PostingLogs.OPERATION_FAILED, function="get_Nposts_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)
        
        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database query failed."
        )

    except Exception as e:
        log_state(PostingLogs.OPERATION_FAILED, function="get_Nposts_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)
        
        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(PostingLogs.EXITING_POSTING_SERVICE, function="get_Nposts", user_id=user_payload.user_id, level=LogState.INFO)

async def create_post_service(user_payload, db: AsyncSession, new_post: PostCreateSchema) -> APIResponse:
    log_state(PostingLogs.POSTING_SERVICE_STARTED, function="create_post_service", user_id=user_payload.user_id, level=LogState.INFO)
    try:
        current_user = user_payload.model_dump()
        log_state(PostingLogs.CREATING_POST, function="create_post_service", user_id=current_user["user_id"], level=LogState.INFO)

        post = PostTable(user_id=current_user["user_id"], **new_post.model_dump()) #Adding data to db's this table btw!
        db.add(post)

        await db.commit()
        await db.refresh(post)

        log_state(PostingLogs.EXECUTING_DATABASE_QUERY, function="create_post_service", user_id=current_user["user_id"], level=LogState.INFO)
        result = await db.execute(
            select(PostTable)
            .options(joinedload(PostTable.owner))
            .where(PostTable.post_id == post.post_id))


        post_with_owner = result.scalar_one()
        log_state(PostingLogs.SUCCESS, function="create_post_service", user_id=current_user["user_id"], level=LogState.INFO)
        

        return APIResponse(
            success=True,
            data=post_with_owner,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        await db.rollback()
        log_state(PostingLogs.OPERATION_FAILED, function="create_post_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database operational failure. Verify data formats and sizes."
        )

    except Exception as e:
        await db.rollback()
        log_state(PostingLogs.OPERATION_FAILED, function="create_post_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(PostingLogs.EXITING_POSTING_SERVICE, function="create_post_service", user_id=user_payload.user_id, level=LogState.INFO)

async def fetch_post_by_id_service(user_payload, db: AsyncSession, id: int) -> APIResponse:

    log_state(PostingLogs.POSTING_SERVICE_STARTED, function="fetch_post_by_id_service", user_id=user_payload.user_id)
    log_state(PostingLogs.FETCHING_POST, function="fetch_post_by_id_service", user_id=user_payload.user_id)

    try:
        post_alias = aliased(PostTable, name="post")

        stmt = (
            select(
                post_alias,
                func.count(LikeTable.post_id).label("likes")
            )
            .join(
                LikeTable,
                LikeTable.post_id == post_alias.post_id,
                isouter=True
            )
            .where(post_alias.post_id == id)
            .group_by(post_alias.post_id)
        )

        log_state(PostingLogs.EXECUTING_DATABASE_QUERY, function="fetch_post_by_id_service", user_id=user_payload.user_id)
        result = await db.execute(stmt)
        post = result.first()

        if not post:
            log_state(PostingLogs.OPERATION_FAILED, function="fetch_post_by_id_service", user_id=user_payload.user_id, level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                error_message="Post not found."
            )

        log_state(PostingLogs.SUCCESS, function="fetch_post_by_id_service", user_id=user_payload.user_id)
        

        return APIResponse(
            success=True,
            data=post,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        log_state(PostingLogs.OPERATION_FAILED, function="fetch_post_by_id_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database query failed."
        )

    except Exception as e:
        log_state(PostingLogs.OPERATION_FAILED, function="fetch_post_by_id_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(PostingLogs.EXITING_POSTING_SERVICE, function="fetch_post_by_id_service", user_id=user_payload.user_id)

async def delete_post_by_id_service(user_payload, db: AsyncSession, id: int) -> APIResponse:
    log_state(PostingLogs.POSTING_SERVICE_STARTED, function="delete_post_by_id_service", user_id=user_payload.user_id)
    log_state(PostingLogs.DELETING_POST, function="delete_post_by_id_service", user_id=user_payload.user_id)

    try:
        current_user = user_payload.model_dump()
        log_state(PostingLogs.EXECUTING_DATABASE_QUERY, function="delete_post_by_id_service", user_id=current_user["user_id"])

        result = await db.execute(
            select(PostTable).where(PostTable.post_id == id)
        )
        post = result.scalar_one_or_none()

        if not post:
            log_state(PostingLogs.OPERATION_FAILED, function="delete_post_by_id_service", user_id=current_user["user_id"], level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                error_message="Post not found."
            )

        log_state(PostingLogs.AUTHORIZATION_CHECK, function="delete_post_by_id_service", user_id=current_user["user_id"])

        if post.user_id != current_user["user_id"]:
            log_state(PostingLogs.OPERATION_FAILED, function="delete_post_by_id_service", user_id=current_user["user_id"], level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNAUTHORIZED_ACCESS.value,
                error_message="Not authorized to delete this post."
            )

        await db.delete(post)
        await db.commit()

        log_state(PostingLogs.SUCCESS, function="delete_post_by_id_service", user_id=current_user["user_id"])
        

        return APIResponse(
            success=True,
            data=None,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        await db.rollback()

        log_state(PostingLogs.OPERATION_FAILED, function="delete_post_by_id_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database operation failed."
        )

    except Exception as e:
        await db.rollback()

        log_state(PostingLogs.OPERATION_FAILED, function="delete_post_by_id_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(PostingLogs.EXITING_POSTING_SERVICE, function="delete_post_by_id_service", user_id=user_payload.user_id)

async def update_post_by_id_service(user_payload, db: AsyncSession, id: int, post_data: PostCreateSchema) -> APIResponse:
    log_state(PostingLogs.POSTING_SERVICE_STARTED, function="update_post_by_id_service", user_id=user_payload.user_id)
    log_state(PostingLogs.UPDATING_POST, function="update_post_by_id_service", user_id=user_payload.user_id)

    try:
        current_user = user_payload.model_dump()
        new_data = post_data.model_dump()

        log_state(PostingLogs.EXECUTING_DATABASE_QUERY, function="update_post_by_id_service", user_id=current_user["user_id"])
        result = await db.execute(
            select(PostTable).where(PostTable.post_id == id)
        )
        fetched_post = result.scalar_one_or_none()

        if not fetched_post:
            log_state(PostingLogs.OPERATION_FAILED, function="update_post_by_id_service", user_id=current_user["user_id"], level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                error_message=f"Post with id {id} was not found."
            )

        log_state(PostingLogs.AUTHORIZATION_CHECK, function="update_post_by_id_service", user_id=current_user["user_id"])

        if fetched_post.user_id != current_user["user_id"]:
            log_state(PostingLogs.OPERATION_FAILED, function="update_post_by_id_service", user_id=current_user["user_id"], level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNAUTHORIZED_ACCESS.value,
                error_message="Not authorized to update this post."
            )

        for key, value in new_data.items():
            setattr(fetched_post, key, value)

        await db.commit()
        await db.refresh(fetched_post)

        result = await db.execute(
            select(PostTable)
            .options(joinedload(PostTable.owner))
            .where(PostTable.post_id == id)
        )
        fetched_post = result.scalar_one()

        log_state(PostingLogs.SUCCESS, function="update_post_by_id_service", user_id=current_user["user_id"])
        

        return APIResponse(
            success=True,
            data=fetched_post,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        await db.rollback()

        log_state(PostingLogs.OPERATION_FAILED, function="update_post_by_id_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database operation failed."
        )

    except Exception as e:
        await db.rollback()

        log_state(PostingLogs.OPERATION_FAILED, function="update_post_by_id_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(PostingLogs.EXITING_POSTING_SERVICE, function="update_post_by_id_service", user_id=user_payload.user_id)

async def create_comment_service(user_payload, post_id: int, db: AsyncSession, comment_data: CommentCreateSchema) -> APIResponse:
    log_state(PostingLogs.POSTING_SERVICE_STARTED, function="create_comment_service", user_id=user_payload.user_id)
    log_state(PostingLogs.CREATING_COMMENT, function="create_comment_service", user_id=user_payload.user_id)

    try:
        current_user = user_payload.model_dump()
        log_state(PostingLogs.EXECUTING_DATABASE_QUERY, function="create_comment_service", user_id=current_user["user_id"])

        result = await db.execute(
            select(PostTable).where(PostTable.post_id == post_id)
        )
        target_post = result.scalar_one_or_none()

        if not target_post:
            log_state(PostingLogs.OPERATION_FAILED, function="create_comment_service", user_id=current_user["user_id"], level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                error_message="Target post does not exist."
            )

        if not target_post.published:
            log_state(PostingLogs.OPERATION_FAILED, function="create_comment_service", user_id=current_user["user_id"], level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNAUTHORIZED_ACCESS.value,
                error_message="Cannot add comments to an unpublished private draft."
            )

        log_state(PostingLogs.VALIDATING_REQUEST, function="create_comment_service", user_id=current_user["user_id"])

        if len(comment_data.text.strip()) == 0:
            log_state(PostingLogs.OPERATION_FAILED, function="create_comment_service", user_id=current_user["user_id"], level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNSUPPORTED_INPUT.value,
                error_message="Comment cannot be empty."
            )

        new_comment = CommentTable(
            text=comment_data.text,
            user_id=current_user["user_id"],
            post_id=post_id
        )

        db.add(new_comment)
        await db.commit()
        await db.refresh(new_comment)

        result = await db.execute(
            select(CommentTable)
            .options(joinedload(CommentTable.commenter))
            .where(CommentTable.comment_id == new_comment.comment_id)
        )

        comment_with_user = result.scalar_one()
        log_state(PostingLogs.SUCCESS, function="create_comment_service", user_id=current_user["user_id"])
        

        return APIResponse(
            success=True,
            data=comment_with_user,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        await db.rollback()
        log_state(PostingLogs.OPERATION_FAILED, function="create_comment_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database operation failed."
        )

    except Exception as e:
        await db.rollback()
        log_state(PostingLogs.OPERATION_FAILED, function="create_comment_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)
        

        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(PostingLogs.EXITING_POSTING_SERVICE, function="create_comment_service", user_id=user_payload.user_id)

async def get_post_comments_service(user_payload, post_id: int, db: AsyncSession, limit: int = 10, offset: int = 0, search: Optional[str] = None) -> APIResponse:

    log_state(PostingLogs.POSTING_SERVICE_STARTED, function="get_post_comments_service", user_id=user_payload.user_id)
    log_state(PostingLogs.FETCHING_COMMENTS, function="get_post_comments_service", user_id=user_payload.user_id)

    try:
        log_state(PostingLogs.VALIDATING_REQUEST, function="get_post_comments_service", user_id=user_payload.user_id)
        if limit <= 0:
            log_state(PostingLogs.OPERATION_FAILED, function="get_post_comments_service", user_id=user_payload.user_id, level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNSUPPORTED_INPUT.value,
                error_message="Limit must be greater than zero."
            )

        log_state(PostingLogs.EXECUTING_DATABASE_QUERY, function="get_post_comments_service", user_id=user_payload.user_id)
        result = await db.execute(
            select(PostTable).where(PostTable.post_id == post_id)
        )
        target_post = result.scalar_one_or_none()

        if not target_post:
            log_state(PostingLogs.OPERATION_FAILED, function="get_post_comments_service", user_id=user_payload.user_id, level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                error_message="Target post does not exist."
            )

        stmt = (
            select(CommentTable)
            .options(joinedload(CommentTable.commenter))
            .where(CommentTable.post_id == post_id)
        )

        if search:
            stmt = stmt.where(CommentTable.text.contains(search))

        stmt = stmt.offset(offset).limit(limit)
        result = await db.execute(stmt)
        comments = result.scalars().all()

        log_state(PostingLogs.SUCCESS, function="get_post_comments_service", user_id=user_payload.user_id)
        

        return APIResponse(
            success=True,
            data=comments,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        log_state(PostingLogs.OPERATION_FAILED, function="get_post_comments_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)
        
        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database query failed."
        )

    except Exception as e:
        log_state(PostingLogs.OPERATION_FAILED, function="get_post_comments_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)
        
        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(PostingLogs.EXITING_POSTING_SERVICE, function="get_post_comments_service", user_id=user_payload.user_id)

async def delete_commentById_service(post_id: int, db: AsyncSession, comment_id: int, user_payload) -> APIResponse:
    log_state(PostingLogs.POSTING_SERVICE_STARTED, function="delete_comment_service", user_id=user_payload.user_id)
    log_state(PostingLogs.DELETING_COMMENT, function="delete_comment_service", user_id=user_payload.user_id)
    

    try:
        current_user = user_payload.model_dump()
        log_state(PostingLogs.EXECUTING_DATABASE_QUERY, function="delete_comment_service", user_id=current_user["user_id"])

        result = await db.execute(
            select(CommentTable).where(
                CommentTable.comment_id == comment_id,
                CommentTable.post_id == post_id
            )
        )
        comment = result.scalar_one_or_none()

        if not comment:
            log_state(PostingLogs.OPERATION_FAILED, function="delete_comment_service", user_id=current_user["user_id"], level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.RESOURCE_NOT_FOUND.value,
                error_message="Comment not found."
            )

        log_state(PostingLogs.AUTHORIZATION_CHECK, function="delete_comment_service", user_id=current_user["user_id"])
        
        if comment.user_id != current_user["user_id"]:
            log_state(PostingLogs.OPERATION_FAILED, function="delete_comment_service", user_id=current_user["user_id"], level=LogState.WARNING)
            

            return APIResponse(
                success=False,
                data=None,
                error_code=USER_ERROR_CODES.UNAUTHORIZED_ACCESS.value,
                error_message="Not authorized to delete this comment."
            )

        await db.delete(comment)
        await db.commit()

        log_state(PostingLogs.SUCCESS, function="delete_comment_service", user_id=current_user["user_id"])
        
        return APIResponse(
            success=True,
            data=None,
            error_code=None,
            error_message=None
        )

    except SQLAlchemyError as e:
        await db.rollback()

        log_state(PostingLogs.OPERATION_FAILED, function="delete_comment_service", user_id=user_payload.user_id, level=LogState.ERROR, exc=e)
        
        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.DATABASE_ERROR.value,
            error_message="Database operation failed."
        )

    except Exception as e:
        await db.rollback()
        log_state(PostingLogs.OPERATION_FAILED, function="delete_comment_service", user_id=user_payload.user_id, level=LogState.EXCEPTION, exc=e)
        
        return APIResponse(
            success=False,
            data=None,
            error_code=SYSTEM_ERROR_CODES.UNKNOWN_ERROR.value,
            error_message="Unexpected server error."
        )

    finally:
        log_state(PostingLogs.EXITING_POSTING_SERVICE, function="delete_comment_service", user_id=user_payload.user_id)