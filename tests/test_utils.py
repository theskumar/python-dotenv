from dotenv import get_cli_string as c


def test_to_cli_string():
    assert c() == 'dotenv'
    assert c(path='/etc/.env') == 'dotenv -f /etc/.env'
    assert c(path='/etc/.env', action='list') == 'dotenv -f /etc/.env list'
    assert c(action='list') == 'dotenv list'
    assert c(action='get', key_value='DEBUG') == 'dotenv get DEBUG'
    assert c(action='set', key_value='DEBUG=True') == 'dotenv set DEBUG True'
    assert c(action='set', key_value='SECRET==@asdfasf') == 'dotenv set SECRET =@asdfasf'
