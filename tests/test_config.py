import os
import pytest
from config import Config

@pytest.fixture
def app_config():
    return Config()

def test_secret_key(app_config):
    assert app_config.SECRET_KEY is not None
    assert app_config.SECRET_KEY != 'you-will-never-guess'

def test_base_dir(app_config):
    assert os.path.exists(app_config.BASE_DIR)

def test_data_dir(app_config):
    assert os.path.exists(app_config.DATA_DIR)
    assert app_config.DATA_DIR.endswith('data')

def test_upload_folder(app_config):
    assert os.path.exists(app_config.UPLOAD_FOLDER)
    assert app_config.UPLOAD_FOLDER.endswith('uploads')

def test_allowed_extensions(app_config):
    assert app_config.ALLOWED_EXTENSIONS == {'png', 'svg', 'pdf', 'jpg', 'csv', 'xls', 'xlsx'}

def test_allowed_documentation_extensions(app_config):
    assert app_config.ALLOWED_DOCUMENTATION_EXTENSIONS == {'png', 'svg', 'pdf', 'jpg'}

def test_allowed_import_extensions(app_config):
    assert app_config.ALLOWED_IMPORT_EXTENSIONS == {'csv', 'xls', 'xlsx'}

def test_max_content_length(app_config):
    assert app_config.MAX_CONTENT_LENGTH == 5 * 1024 * 1024  # 5 MB

def test_json_file_paths(app_config):
    json_files = ['USERS_FILE', 'PROPERTIES_FILE', 'TRANSACTIONS_FILE', 'CATEGORIES_FILE', 'REIMBURSEMENTS_FILE']
    for file in json_files:
        assert hasattr(app_config, file)
        assert os.path.exists(getattr(app_config, file))
        assert getattr(app_config, file).endswith('.json')

def test_properties_file_path(app_config):
    assert app_config.PROPERTIES_FILE.endswith(os.path.join('data', 'properties.json'))

def test_geoapify_api_key(app_config):
    assert hasattr(app_config, 'GEOAPIFY_API_KEY')
    assert app_config.GEOAPIFY_API_KEY == 'f9577704874047cd8fc962b020db0d20'

def test_environment_variables():
    original_secret_key = os.environ.get('SECRET_KEY')
    os.environ['SECRET_KEY'] = 'test_secret_key'
    config = Config()
    assert config.SECRET_KEY == 'test_secret_key'
    if original_secret_key:
        os.environ['SECRET_KEY'] = original_secret_key
    else:
        del os.environ['SECRET_KEY']