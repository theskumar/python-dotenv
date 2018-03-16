from dotenv import get_cli_string as c


def test_to_cli_string():
    assert c() == 'dotenv'
    assert c(path='/etc/.env') == 'dotenv -f /etc/.env'
    assert c(path='/etc/.env', action='list') == 'dotenv -f /etc/.env list'
    assert c(action='list') == 'dotenv list'
    assert c(action='get', key='DEBUG') == 'dotenv get DEBUG'
    assert c(action='set', key='DEBUG', value='True') == 'dotenv set DEBUG True'
    assert c(action='set', key='SECRET', value='=@asdfasf') == 'dotenv set SECRET =@asdfasf'
    assert c(action='set', key='SECRET', value='a b') == 'dotenv set SECRET "a b"'
    assert c(action='set', key='SECRET', value='a b', quote="always") == 'dotenv -q always set SECRET "a b"'
