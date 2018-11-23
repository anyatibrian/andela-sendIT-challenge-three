import json
import pytest
from Api import create_app
from Api.models.database import DBConnect
from tests import test_base
from Api.models.users import Users


# creating our test client
@pytest.fixture(scope='module')
def client():
    app = create_app()
    test_client = app.test_client()

    # creating the database object
    db = DBConnect()
    db.create_tables()
    # establishing the application context
    cxt = app.app_context()
    cxt.push()
    yield test_client
    db.drop_tables()
    cxt.pop()


# fixtures that registers the users
@pytest.fixture(scope='module')
def register_user(client, username='anyatibrian', password='password@123', email='anyatbrian@gmail.com'):
    data = {
        'username': username,
        'password': password,
        'email': email
    }
    return client.post('api/v1/auth/signup', data=json.dumps(data))


# fixture that logs in users
@pytest.fixture(scope='module')
def login_user(client, username='anyatibrian', password='password@123'):
    data = {
        'username': username,
        'password': password,
    }
    return client.post('api/v1/auth/login', data=json.dumps(data))


@pytest.fixture(scope='module')
def login_admin(client, username='admin', password='admin@123'):
    data = {
        'username': username,
        'password': password,
    }
    return client.post('api/v1/auth/login', data=json.dumps(data))


@pytest.fixture(scope='module')
def register_admin():
    admin = Users().create_default_admmin()
    return admin


@pytest.fixture(scope='module')
def login_admin(client, username='admin', password='admin@123'):
    data = {
        'username': username,
        'password': password,
    }
    return client.post('api/v1/auth/login', data=json.dumps(data))


def test_user_signup_has_empty_field(client):
    """test that checks for empty field in user input"""
    response = client.post('api/v1/auth/signup', data=json.dumps(test_base.empty_users))
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'some fields are empty'


def test_to_check_for_invalid_users_and_password(client):
    """test that checks for invalid and username length"""
    response = client.post('api/v1/auth/signup', data=json.dumps(test_base.invalide_user))
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'username and password should be atleast six chars'


def test_to_check_for_invalid_email(client):
    response = client.post('api/v1/auth/signup', data=json.dumps(test_base.invalide_email))
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'invalid email'


def test_register_user_endpoints(client):
    """test for registering new users"""
    response = client.post('api/v1/auth/signup', data=json.dumps(test_base.valid_user))
    assert response.status_code == 201
    assert json.loads(response.data)['message'] == 'your account has been created successfully'


def test_user_already_exist_(client):
    """test that checks whether the user has already been created"""
    response = client.post('api/v1/auth/signup', data=json.dumps(test_base.valid_user))
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'anyatibrian@gmail.com already taken'


def test_signup_key_errors(client):
    response = client.post('api/v1/auth/signup', data=json.dumps(test_base.key_value_error))
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'value and key errors'


def test_user_login(client):
    """test user login"""
    response = client.post('api/v1/auth/login', data=json.dumps(test_base.value_error))
    assert response.status_code == 400
    assert json.loads(response.data)['errors'] == 'key and value error'


def test_user_login(client):
    """test user login"""
    response = client.post('api/v1/auth/login', data=json.dumps(test_base.empty_login))
    assert response.status_code == 400
    assert json.loads(response.data)['message'] == 'please enter your username and password'

    # test to checks for valid login
    response = client.post('api/v1/auth/login', data=json.dumps(test_base.valid_login))
    assert response.status_code == 200
    assert json.loads(response.data)['access-token'] == json.loads(response.data)['access-token']

    # test to check for invalid login
    response = client.post('api/v1/auth/login', data=json.dumps(test_base.invalid_login))
    assert response.status_code == 401
    assert json.loads(response.data)['message'] == 'username and password does not exist'

    response = client.post('api/v1/auth/login', data=json.dumps(test_base.bad_user_fields_login))
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'value and key errors'


def test_post_invalid_parcel_endpoints(client, register_user, login_user):
    """test to check for empty parcel order field"""
    register_user
    result = login_user

    access_token = json.loads(result.data.decode())['access-token']
    response = client.post('api/v1/parcels', headers=dict(Authorization="Bearer " + access_token),
                           data=json.dumps(test_base.empty_field))
    assert response.status_code == 400
    assert b'fields must not be empty' in response.data
    # checks for empty field
    response = client.post('api/v1/parcels', headers=dict(Authorization="Bearer " + access_token),
                           data=json.dumps(test_base.white_space))
    assert response.status_code == 400
    assert b'white space chars not allowed' in response.data


def test_for_invalid_desc(client, register_user, login_user):
    """test for invalid parcel orders"""
    register_user
    result = login_user

    access_token = json.loads(result.data.decode())['access-token']
    response = client.post('api/v1/parcels', headers=dict(Authorization="Bearer " + access_token),
                           data=json.dumps(test_base.invalid_desc))
    assert response.status_code == 400
    assert b'your description field has invalid chars' in response.data


def test_test_empty_parcel_endpoints(client, register_user, login_user):
    """test empty parcel list """
    register_user
    result = login_user

    access_token = json.loads(result.data.decode())['access-token']
    response = client.get('api/v1/parcels', headers=dict(Authorization="Bearer " + access_token))
    assert response.status_code == 404
    assert b'your order is empty' in response.data


def test_post_parcel_order_endpoints(client, register_user, login_user):
    """test parcel order """
    register_user
    result = login_user

    access_token = json.loads(result.data.decode())['access-token']
    response = client.post('api/v1/parcels', headers=dict(Authorization="Bearer " + access_token),
                           data=json.dumps(test_base.parcel_data))
    assert response.status_code == 201
    assert b'parcel order created successfully' in response.data


def test_get_all_parcel_orders(client, register_user, login_user):
    """test get all parcel endpoints """
    register_user
    result = login_user

    access_token = json.loads(result.data.decode())['access-token']
    response = client.get('api/v1/parcels', headers=dict(Authorization="Bearer " + access_token))
    assert response.status_code == 200
    assert json.loads(response.data)['parcel_orders'][0]['destination'] == 'lira'


def test_get_single_order_endpoint(client, login_user, register_user):
    """test user get single order endpoint"""
    register_user
    result = login_user

    access_token = json.loads(result.data.decode())['access-token']
    response = client.get('api/v1/parcels/1', headers=dict(Authorization="Bearer " + access_token))
    assert response.status_code == 200
    response = client.get('api/v1/parcels/1000', headers=dict(Authorization="Bearer " + access_token))
    assert response.status_code == 404
    assert b'parcel order not found' in response.data


def test_update_parcel_destination(client, register_user, login_user):
    register_user
    result = login_user

    access_token = json.loads(result.data.decode())['access-token']
    response = client.put('api/v1/parcels/1/destination', headers=dict(Authorization="Bearer " + access_token),
                          data=json.dumps({'destination': 'Kampala'}))
    assert response.status_code == 201
    response = client.put('api/v1/parcels/1/destination', headers=dict(Authorization="Bearer " + access_token),
                          data=json.dumps({'destination': 10000}))
    assert response.status_code == 400
    assert b'destination should be strings only' in response.data


def test_update_order_status_endpoint(client, register_user, login_user):
    """the function that test user update order status endpoints"""
    register_user
    result = login_user

    access_token = json.loads(result.data.decode())['access-token']
    response = client.put('api/v1/parcels/1', headers=dict(Authorization="Bearer " + access_token),
                          data=json.dumps({'status': 'canceled'}))
    assert response.status_code == 201
    assert b'status has been successfully updated' in response.data
    access_token = json.loads(result.data.decode())['access-token']
    response = client.put('api/v1/parcels/1', headers=dict(Authorization="Bearer " + access_token),
                          data=json.dumps({'status': 'cance'}))
    assert response.status_code == 400


def test_not_admin(client, register_user, login_user):
    register_user
    result = login_user

    access_token = json.loads(result.data.decode())['access-token']
    response = client.get('api/v1/admin/parcels', headers=dict(Authorization="Bearer " + access_token))
    assert b'You cant perform this action because you are unauthorised' in response.data


def test_get_all_admin_parcels(client, register_admin, login_admin):
    register_admin
    result = login_admin

    access_token = json.loads(result.data.decode())['access-token']
    response = client.get('api/v1/admin/parcels', headers=dict(Authorization="Bearer " + access_token))
    assert response.status_code == 200


def test_update_present_location(client, register_admin, login_admin):
    register_admin
    result = login_admin

    access_token = json.loads(result.data.decode())['access-token']
    response = client.put('api/v1/parcels/1/presentLocation', headers=dict(Authorization="Bearer " + access_token),
                          data=json.dumps({'current_location': '00000'}))
    assert response.status_code == 400

    response = client.put('api/v1/parcels/1/presentLocation', headers=dict(Authorization="Bearer " + access_token),
                          data=json.dumps({'current_location': 'lira'}))
    assert response.status_code == 201


def test_admin_update_status(client, register_admin, login_admin):
    register_admin
    result = login_admin

    access_token = json.loads(result.data.decode())['access-token']
    response = client.put('api/v1/parcels/1/status', headers=dict(Authorization="Bearer " + access_token),
                          data=json.dumps({'status': 'canceled'}))
    assert response.status_code == 400

    response = client.put('api/v1/parcels/1/status', headers=dict(Authorization="Bearer " + access_token),
                          data=json.dumps({'status': 'Transit'}))
    assert response.status_code == 201