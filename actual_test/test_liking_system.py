import pytest

def test_likes_on_posts(auth_client_factory, test_users, test_posts):
    user1 = test_users("121@gmail.com", "woohShii")
    authed_u = auth_client_factory(user1)
    
    res = authed_u.post("/likes/", json={"post_id": test_posts[0].post_id, "dir": 1})
    assert res.status_code == 200


@pytest.fixture
def like_factory(auth_client_factory):
    def create_like(user, post_id):
        client = auth_client_factory(user)
        res = client.post(
            "/likes/",
            json={"post_id": post_id, "dir": 1}
        )
        return res
    return create_like


def test_liked_twice_check(like_factory, seeded_users, test_posts):
    user = seeded_users["user1"]
    post_id = test_posts[0].post_id

    r1 = like_factory(user, post_id)
    r2 = like_factory(user, post_id)

    assert r1.status_code == 200
    assert r2.status_code == 409


def test_delete_like(seeded_users, test_posts, auth_client_factory):
    user1 = seeded_users["user1"]
    client = auth_client_factory(user1)
    post_id = test_posts[0].post_id

    res1 = client.post("/likes/", json={"post_id": post_id, "dir": 1})
    assert res1.status_code == 200

    res2 = client.post("/likes/", json={"post_id": post_id, "dir": 0})
    assert res2.status_code == 200


def test_unlike_already_unliked(seeded_users, test_posts, auth_client_factory):
    user1 = seeded_users["user1"]
    client = auth_client_factory(user1)
    post_id = test_posts[0].post_id

    r1 = client.post("/likes/", json={"post_id": post_id, "dir": 1})
    assert r1.status_code == 200

    r2 = client.post("/likes/", json={"post_id": post_id, "dir": 0})
    assert r2.status_code == 200

    r3 = client.post("/likes/", json={"post_id": post_id, "dir": 0})
    assert r3.status_code == 404
    assert r3.json()["detail"] == "Like does not exist, try liking the post before unliking..."


def test_like_non_existing_post(seeded_users, test_posts, auth_client_factory):
    user1 = seeded_users["user1"]
    auted_user = auth_client_factory(user1)
    fake_id = 5748456
    
    res = auted_user.post("/likes/", json={"post_id": fake_id, "dir": 1})
    assert res.status_code == 404