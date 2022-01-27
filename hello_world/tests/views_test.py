from django.test.client import Client


class TestHelloWorldView:
    """ Hello Worldのviewが呼び出せるか """

    # ステータスコードは正常か
    def test_status_200(self):
        # GIVEN
        client = Client()
        # WHEN
        actual = client.get('/')
        # THEN
        assert actual.status_code == 200
