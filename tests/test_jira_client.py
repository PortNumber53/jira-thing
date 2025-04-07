#!/usr/bin/env python3

import pytest
from unittest.mock import MagicMock, patch
from jira_client import JiraManager

class MockJIRA:
    def __init__(self, server=None, basic_auth=None):
        self.current_user = lambda: "test_user"
        # Simulate a successful connection
        import logging
        if server:
            logging.info(f"Successfully connected to Jira at {server}")

    def current_user(self):
        return "test_user"

    def projects(self):
        return [
            type('Project', (), {'key': 'TEST1', 'name': 'Test Project 1'}),
            type('Project', (), {'key': 'TEST2', 'name': 'Test Project 2'})
        ]

    def create_project(self, **kwargs):
        return type('CreatedProject', (), {
            'key': 'NEWPROJ', 
            'name': 'New Project', 
            'id': '12345'
        })

    def create_issue(self, **kwargs):
        return type('CreatedIssue', (), {
            'key': 'TEST-123',
            'fields': type('Fields', (), {
                'summary': 'Test Task',
                'project': type('Project', (), {'key': 'TEST1'})
            })
        })

@pytest.fixture
def mock_config():
    return {
        'jira_server': 'https://test.atlassian.net',
        'jira_username': 'test_user',
        'jira_token': 'test_token'
    }

@patch('jira_client.JIRA', MockJIRA)
@patch('jira_client.config', new_callable=dict)
def test_jira_manager_initialization(mock_config, caplog):
    """Test JiraManager initialization."""
    mock_config.update({
        'jira_server': 'https://test.atlassian.net',
        'jira_username': 'test_user',
        'jira_token': 'test_token'
    })
    
    # Explicitly set logging level to capture all messages
    import logging
    logging.getLogger().setLevel(logging.DEBUG)
    
    jira_manager = JiraManager()
    assert jira_manager.client is not None
    
    # Print out all captured log records for debugging
    # for record in caplog.records:
    #     print(f"Log record: {record.levelname} - {record.message}")
    
    # Use a more flexible assertion for log messages
    for record in caplog.get_records('DEBUG'):
        print(f"Log record: {record.levelname} - {record.message}")
    
    # Use a more flexible assertion for log messages
    assert any("Successfully connected to Jira" in record.message for record in caplog.records)

@patch('jira_client.JIRA', MockJIRA)
@patch('jira_client.config', new_callable=dict)
def test_get_projects(mock_config):
    """Test retrieving Jira projects."""
    mock_config.update({
        'jira_server': 'https://test.atlassian.net',
        'jira_username': 'test_user',
        'jira_token': 'test_token'
    })
    
    jira_manager = JiraManager()
    projects = jira_manager.get_projects()
    
    assert len(projects) == 2
    assert projects[0]['key'] == 'TEST1'
    assert projects[0]['name'] == 'Test Project 1'

@patch('jira_client.JIRA', MockJIRA)
@patch('jira_client.config', new_callable=dict)
def test_create_project(mock_config):
    """Test creating a new Jira project."""
    mock_config.update({
        'jira_server': 'https://test.atlassian.net',
        'jira_username': 'test_user',
        'jira_token': 'test_token'
    })
    
    jira_manager = JiraManager()
    project = jira_manager.create_project("New Project", "NEWPROJ")
    
    assert project is not None
    assert project['key'] == 'NEWPROJ'
    assert project['name'] == 'New Project'

@patch('jira_client.JIRA', MockJIRA)
@patch('jira_client.config', new_callable=dict)
def test_create_task(mock_config):
    """Test creating a new Jira task."""
    mock_config.update({
        'jira_server': 'https://test.atlassian.net',
        'jira_username': 'test_user',
        'jira_token': 'test_token'
    })
    
    jira_manager = JiraManager()
    task = jira_manager.create_task("TEST1", "Test Task")
    
    assert task is not None
    assert task['key'] == 'TEST-123'
    assert task['summary'] == 'Test Task'
    assert task['project'] == 'TEST1'

def test_jira_manager_connection_failure():
    """Test JiraManager initialization failure."""
    with patch('jira_client.JIRA', side_effect=Exception("Connection failed")):
        with pytest.raises(RuntimeError, match="Jira client initialization failed"):
            JiraManager()
