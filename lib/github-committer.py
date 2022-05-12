import requests
import json
import os
from github import Github
from github import InputGitTreeElement
from git import Repo


def main():

    build_url = os.getenv('BUILD_URL')
    create_pull_request = os.getenv('CREATE_PULL_REQUEST')
    pull_request_branch = os.getenv('PULL_REQUEST_BRANCH')
    directory = os.getenv('WORKING_DIRECTORY')
    organization = os.getenv('REPO_OWNER')
    repository = os.getenv('REPO_NAME')
    target_branch = os.getenv('TARGET_BRANCH')
    target_file_path_prefix = os.getenv('TARGET_FILE_PATH_PREFIX')
    token = os.getenv('GITHUB_TOKEN')
    file = os.getenv('FILE')
    file_path = os.path.join(directory, file)
    target_file_path = os.path.join(target_file_path_prefix, file)
    feature_branch = target_branch

    # Set GitHub repository
    repo = '{}/{}'.format(organization, repository)

    # PyGitHub Auth
    g = Github(token)

    # Connect to GitHub repository
    print('Connecting to repository: {}'.format(repo))
    repo = g.get_repo(repo)

    commit_message = 'Promoting Changes To: {} Promotion Build: {}'.format(file, build_url)

    if create_pull_request:
        # Check for PR branch
        print('Checking for Branch: {}...'.format(pull_request_branch))
        feature_branch = pull_request_branch
        try:
            repo.get_branch(branch=pull_request_branch)
        except:
            print('Branch NOT Found')
            # Get target branch's latest SHA
            target_contents = repo.get_branch(target_branch)
            print('Creating Branch {} using SHA {}'.format(pull_request_branch, target_contents.commit.sha))
            # Create branch
            repo.create_git_ref(ref='refs/heads/' + pull_request_branch, sha=target_contents.commit.sha)
            pass

    print('Gathering Target File {} for Target Branch {}'.format(file, feature_branch))
    original_contents = repo.get_contents(target_file_path, ref=feature_branch)

    new_contents = open(file_path, 'r').read()

    # Update File
    print('Updating {} on Branch {}'.format(original_contents.path, feature_branch))
    repo.update_file(original_contents.path, commit_message, new_contents, original_contents.sha, branch=feature_branch)

    # Pull Request
    if create_pull_request:
        # Check for existing/open pull request
        print('Checking for Open Pull Request...')
        check_for_prs = repo.get_pulls(state='open', head=feature_branch, base=target_branch)
        if check_for_prs.totalCount != 0:
            for pr in check_for_prs:
                print('Found Open Pull Request.')
                print('Name: {}'.format(pr.title))
                print('Number: {}'.format(pr.number))
        else:
            print('Opening Pull Request.')
            # Create pull request
            create_pull = repo.create_pull(title='Pull Request from GitOps Step, Build URL: {}'.format(build_url), head=feature_branch, base=target_branch, body='Automated Pull Request from Build: {}'.format(build_url), maintainer_can_modify=True)

            # Get pull request information
            print('Created Pull Request: {}'.format(repo.get_pull(create_pull.number)))

if __name__ == "__main__":
    main()
