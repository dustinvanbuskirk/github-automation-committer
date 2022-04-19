import requests
import json
import os
from github import Github
from github import InputGitTreeElement
from git import Repo


def main():

    branch = os.getenv('BRANCH')
    build_id = os.getenv('BUILD_URL')
    create_pull_request = os.getenv('CREATE_PULL_REQUEST')
    directory = os.getenv('WORKING_DIRECTORY')
    organization = os.getenv('REPO_OWNER')
    repository = os.getenv('REPO_NAME')
    orig_ref = os.getenv('REF', branch)
    target_branch = os.getenv('TARGET_BRANCH')
    token=os.getenv('GITHUB_TOKEN')
    file = os.getenv('FILE')
    file_path = os.path.join(directory, repository, file)

    # Fetch GIT Creedentials

    repo_dir = os.path.join(directory, repository)
    repo = '{}/{}'.format(organization, repository)

    # PyGitHub Auth
    g = Github(token)

    # Set repository
    repo = g.get_repo(repo)

    # Create commit
    target_file = (file)

    commit_message = 'Commit created by Codefresh Build: {}'.format(build_id)

    original_contents = repo.get_contents(target_file, ref=orig_ref)

    new_contents = open(file_path, 'r').read()

    repo.update_file(original_contents.path, commit_message, new_contents, original_contents.sha, branch=branch)

    # Basic Auth option for later
    # else:
    #     # Set repository
    #     repo = Repo(repo_dir)

    #     repo.git.checkout(branch)

    #     # Create commit
    #     file_list = [
    #         os.path.join(repo_dir, file)
    #     ]
    #     commit_message = 'Commit created by Codefresh Build: {}'.formatbuild_id)
    #     repo.index.add(file_list)
    #     repo.index.commit(commit_message)

    #     # Push commit
    #     origin = repo.remote('origin')
    #     origin.push()

    if create_pull_request:
        # Check for existing/open pull request
        print('Checking for Open Pull Request...')
        check_for_prs = repo.get_pulls(state='open', head=branch, base=target_branch)
        if check_for_prs.totalCount != 0:
            for pr in check_for_prs:
                print('Found Open Pull Request.')
                print('Name: {}'.format(pr.title))
                print('Number: {}'.format(pr.number))
        else:
            print('Opening Pull Request.')
            # Create pull request
            create_pull = repo.create_pull(title='Pull Request from GitOps Committer Step, Build ID: {}'.format(build_id), head=branch, base=target_branch, body='Automated Pull Request from Jenkins Build: {}'.format(build_id), maintainer_can_modify=True)

            # Get pull request information
            print('Created Pull Request: {}'.format(repo.get_pull(create_pull.number)))


if __name__ == "__main__":
    main()
