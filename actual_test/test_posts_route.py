import pytest
from pydantic import TypeAdapter
from utils.schemas import PostLikesOutSchema, PostResponseSchema

def test_auth_get_all_posts(auth_client_factory, test_users, test_posts: list):
    user1 = test_users("a@gmail.com", "123")
    aut_client = auth_client_factory(user1)
    res = aut_client.get("/posts/")

    assert res.status_code == 200

    for item in res.json():
        post = item["post"]
        assert "title" in post
        assert "content" in post
        assert "post_id" in post
        assert "owner" in post
        assert "likes" in item

    try:
        ta = TypeAdapter(list[PostLikesOutSchema])
        validated_posts = ta.validate_python(res.json())
    except Exception as e:
        pytest.fail(f"API response failed validation: {e}")

    assert all(p.post.title for p in validated_posts)


def test_unauth_get_all_posts(client): 
    res = client.get("/posts/")
    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"
    assert res.headers["WWW-Authenticate"] == "Bearer"  


def test_unauth_gets_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].post_id}")
    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"
    assert res.headers["WWW-Authenticate"] == "Bearer"  


def test_get_post_with_wrong_id(auth_client_factory, test_users):
    wrong_post_id = 54651213
    user1 = test_users("a@gmail.com", "123")
    aut_client = auth_client_factory(user1)

    res = aut_client.get(f"/posts/{wrong_post_id}")
    assert res.status_code == 404


def test_get_post_by_id_authorized(auth_client_factory, test_posts, test_users):
    user1 = test_users("a@gmail.com", "123")
    aut_client = auth_client_factory(user1)

    res = aut_client.get(f"/posts/{test_posts[0].post_id}")

    server_response: dict = res.json()
    ta = TypeAdapter(PostLikesOutSchema)
    validated_post = ta.validate_python(server_response)

    assert validated_post.post.post_id == test_posts[0].post_id
    assert validated_post.post.title == test_posts[0].title
    assert validated_post.post.content == test_posts[0].content


@pytest.mark.parametrize("title, content, published", [
    ("title 1", "contnet 1", True),
    ("title 2", "contnet 2", False),
])
def test_create_post_authed(auth_client_factory, test_users, title, content, published, session):
    user1 = test_users("a@gmail.com", "123")
    aut_client = auth_client_factory(user1)

    res = aut_client.post("/posts/", json={
        "title": title,
        "content": content,
        "published": published
    })

    assert res.status_code == 201


def test_unauth_create_post(client):
    res = client.post("/posts/", json={
        "title": "Pizza are bad???",
        "content": "b4 yall kill me, i meant form x resturant not in genral",
        "published": True
    })

    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"
    assert res.headers["WWW-Authenticate"] == "Bearer"  


def test_unauth_del_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].post_id}")
    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"
    assert res.headers["WWW-Authenticate"] == "Bearer"  


def test_auted_delete_post(auth_client_factory, seeded_users, test_posts):
    user1 = seeded_users["user1"]
    aut_client = auth_client_factory(user1)

    post = test_posts[0]
    res = aut_client.delete(f"/posts/{post.post_id}")

    assert res.status_code == 204


def test_del_non_existant_post(auth_client_factory, test_users):
    fake_id = 485446
    user1 = test_users("a@gmail.com", "123")
    aut_client = auth_client_factory(user1)

    res = aut_client.delete(f"/posts/{fake_id}")
    server_response = res.json()

    assert res.status_code == 404
    assert server_response["detail"] == "Post Not Found!"


def test_try_to_delete_some_else_post(auth_client_factory, test_users, test_posts): 
    user1 = test_users("a@gmail.com", "123")
    aut_client = auth_client_factory(user1)

    res = aut_client.delete(f"/posts/{test_posts[2].post_id}")

    assert res.status_code == 403
    assert res.json()["detail"] == "Not Authorized to delete this post!"


def test_update_post_auth(auth_client_factory, seeded_users, test_posts): 
    user1 = seeded_users["user1"]
    aut_client = auth_client_factory(user1)
    post = test_posts[0]

    data = {
        "title": "new_t1",
        "content": "new_c1",
        "published": True
    }

    res = aut_client.put(f"/posts/{post.post_id}", json=data)
    assert res.status_code == 200

    server_response = res.json()
    ta = TypeAdapter(PostResponseSchema)
    validated_post = ta.validate_python(server_response)

    assert validated_post.title == data["title"]
    assert validated_post.content == data["content"]
    assert validated_post.published == data["published"]
    assert validated_post.post_id == post.post_id
    assert validated_post.user_id == user1["user_id"]


def test_update_other_user_post(auth_client_factory, seeded_users, test_posts):
    user1 = seeded_users["user1"]
    aut_client = auth_client_factory(user1)
    post = test_posts[2]

    data = {
        "title": "Updating a ghost post",
        "content": "This should fail because the ghost died",
        "published": True
    }

    res = aut_client.put(f"/posts/{post.post_id}", json=data)

    assert res.status_code == 403
    assert res.json()["detail"] == "Not Authorized to Update this post"


def test_unauth_update_post(client, test_posts):
    data = {
        "title": "x",
        "content": "y",
        "published": True
    }

    res = client.put(f"/posts/{test_posts[0].post_id}", json=data)

    assert res.status_code == 401
    assert res.json()["detail"] == "Not authenticated"


def test_update_non_existant_post(auth_client_factory, test_users):
    fake_id = 485446
    user1 = test_users("a@gmail.com", "123")
    aut_client = auth_client_factory(user1)
    
    dummy_data = {
        "title": "Ghost Update",
        "content": "Valid body format, but targeting a bad ID",
        "published": True
    }

    res = aut_client.put(f"/posts/{fake_id}", json=dummy_data)
    assert res.status_code == 404



def test_create_comment_success(
    test_user,
    test_posts,
    auth_client_factory
):
    post = test_posts[0]
    user = test_user

    auth_client = auth_client_factory(user)

    payload = {
        "text": "this is a test comment"
    }

    res = auth_client.post(
        f"/posts/{post.post_id}/comments",
        json=payload
    )

    assert res.status_code == 201

    data = res.json()
    assert data["text"] == payload["text"]
    assert data["post_id"] == post.post_id
    assert data["user_id"] == user["user_id"]

    # commenter should exist because of joinedload
    assert "commenter" in data
    assert data["commenter"]["user_id"] == user["user_id"]


def test_create_comment_post_not_found(
    test_user,
    auth_client_factory
):
    user = test_user
    auth_client = auth_client_factory(user)
    payload = {"text": "hello"}

    fake_id = 4864189
    res = auth_client.post(
        f"/posts/{fake_id}/comments",
        json=payload
    )

    assert res.status_code == 404
    assert res.json()["detail"] == "Target post does not exist"


def test_create_comment_unauthorized(
    client,
    test_posts
):
    post = test_posts[0]
    payload = {"text": "no auth comment"}

    res = client.post(
        f"/posts/{post.post_id}/comments",
        json=payload
    )
    assert res.status_code == 401



def test_create_comment_invalid_payload(
    test_user,
    auth_client_factory,
    test_posts
):
    user = test_user
    auth_client = auth_client_factory(user)
    post = test_posts[0]

    payload = {}  # missing text

    res = auth_client.post(
        f"/posts/{post.post_id}/comments",
        json=payload
    )

    assert res.status_code == 422
    assert res.json()["detail"][0]["type"] == "missing"



def test_get_comments_for_post_success(
    test_user,
    test_posts,
    auth_client_factory,
    session
):
    user = test_user
    post = test_posts[0]
    auth_client = auth_client_factory(user)

    # seed comments directly in DB
    from db_tables.tables import CommentTable

    comment1 = CommentTable(
        text="c1",
        user_id=user["user_id"],
        post_id=post.post_id
    )

    comment2 = CommentTable(
        text="c2",
        user_id=user["user_id"],
        post_id=post.post_id
    )

    session.add_all([comment1, comment2])
    session.commit()

    res = auth_client.get(f"/posts/{post.post_id}/comments")
    assert res.status_code == 200

    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 2

    assert data[0]["text"] in ["c1", "c2"]
    assert "commenter" in data[0]
    assert data[0]["commenter"]["user_id"] == user["user_id"]


def test_get_comments_post_not_found(
    test_user,
    test_posts,
    auth_client_factory
):
    user = test_user
    auth_client = auth_client_factory(user)

    res = auth_client.get("/posts/999999/comments")

    assert res.status_code == 404
    assert res.json()["detail"] == "Target post does not exist"


def test_get_comments_unauthorized(
    client,
    test_posts
):
    post = test_posts[0]
    res = client.get(f"/posts/{post.post_id}/comments")

    assert res.status_code == 401


#verify if joinload is actually working
def test_get_comments_includes_commenter(
    test_user,
    test_posts,
    auth_client_factory,
    session
):
    user = test_user
    post = test_posts[0]
    auth_client = auth_client_factory(user)

    from db_tables.tables import CommentTable

    comment = CommentTable(
        text="joinedload test",
        user_id=user["user_id"],
        post_id=post.post_id
    )

    session.add(comment)
    session.commit()

    res = auth_client.get(f"/posts/{post.post_id}/comments")

    assert res.status_code == 200
    data = res.json()[0]

    # commenter must exist because of joinedload
    assert "commenter" in data
    assert data["commenter"]["email"] == user["email"]




def test_delete_comment_success(
    test_user,
    test_posts,
    auth_client_factory,
    session
):
    user = test_user
    post = test_posts[0]
    auth_client = auth_client_factory(user)

    from db_tables.tables import CommentTable

    comment = CommentTable(
        text="to be deleted",
        user_id=user["user_id"],
        post_id=post.post_id
    )

    session.add(comment)
    session.commit()
    session.refresh(comment)

    res = auth_client.delete(
        f"/posts/{post.post_id}/comments/{comment.comment_id}"
    )

    assert res.status_code == 204

    # verify actually deleted
    deleted = session.query(CommentTable).filter(
        CommentTable.comment_id == comment.comment_id
    ).first()

    assert deleted is None


def test_delete_comment_not_found(
    test_user,
    test_posts,
    auth_client_factory
):
    user = test_user
    post = test_posts[0]
    auth_client = auth_client_factory(user)

    res = auth_client.delete(
        f"/posts/{post.post_id}/comments/999999"
    )

    assert res.status_code == 404
    assert res.json()["detail"] == "Comment not found"


def test_delete_comment_forbidden(
    test_user,
    test_posts,
    auth_client_factory,
    test_users,
    session
):
    user1 = test_user
    user2 = test_users("other@email.com", "otherpass")

    post = test_posts[0]

    from db_tables.tables import CommentTable

    # comment created by user2
    comment = CommentTable(
        text="not yours",
        user_id=user2["user_id"],
        post_id=post.post_id
    )

    session.add(comment)
    session.commit()
    session.refresh(comment)

    auth_client = auth_client_factory(user1)

    res = auth_client.delete(
        f"/posts/{post.post_id}/comments/{comment.comment_id}"
    )

    assert res.status_code == 403
    assert res.json()["detail"] == "Not authorized to delete this comment"