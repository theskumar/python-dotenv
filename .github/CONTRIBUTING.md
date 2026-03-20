# Contributing to python-dotenv

We welcome you to [check the existing issues](https://github.com/theskumar/python-dotenv/issues) for bugs or enhancements to work on.
If you have an idea for an extension to python-dotenv, please [file a new issue](https://github.com/theskumar/python-dotenv/issues/new) so we can discuss it.

Make sure to familiarize yourself with the project layout before making any major contributions.

## How to contribute

1. Fork the [project repository](https://github.com/theskumar/python-dotenv/): click on the 'Fork' button near the top of the page. This creates a copy of the code under your account on the GitHub server.

2. Clone this copy to your local disk:

   ```bash
   git clone git@github.com:YourUsername/python-dotenv.git
   ```

3. Create a branch to hold your changes:

   ```bash
   git checkout -b my-contribution
   ```

4. Make sure your local environment is correctly set up for development and that all required project dependencies are installed.

5. Start making changes on your newly created branch, remembering to
   never work on the ``master`` branch! Work on this copy on your
   computer using Git to do the version control.

6. To check that your changes haven’t broken existing tests and that new tests pass, run the tests.

7. When you're done editing and local testing, run:

   ```bash
   git add modified_files
   git commit
   ```

   to record your changes in Git, then push them to GitHub with:

   ```bash
   git push -u origin my-contribution
   ```

Finally, go to the web page of your fork of the python-dotenv repo, and click
'Pull Request' (PR) to send your changes to the maintainers for review.

When creating your PR, please make sure to enable the "Allow edits from maintainers" option (known as maintainer_can_modify).
This allows the maintainers to make minor changes or improvements to your PR branch if necessary during the review process.

(If it looks confusing to you, then look up the [Git
documentation](http://git-scm.com/documentation) on the web.)

## Before submitting your pull request

Before you submit a pull request for your contribution, please work
through this checklist to make sure that you have done everything
necessary so we can efficiently review and accept your changes.

If your contribution changes python-dotenv in any way:

- Update the [documentation](https://saurabh-kumar.com/python-dotenv/) so all of your changes are reflected there.

- Update the [README](https://github.com/theskumar/python-dotenv/tree/main/README.md) if anything there has changed.

If your contribution involves any code changes:

- Update the [project tests](https://github.com/theskumar/python-dotenv/tree/main/.github/workflows/test.yml) to test your code changes.

- Make sure that your code is properly commented with [docstrings](https://peps.python.org/pep-0257/) and comments explaining your rationale behind non-obvious coding practices.

## Acknowledgements

This document guide is based at well-written contributung guide of [TPOT](https://github.com/EpistasisLab/tpot) and [FEDOT](https://github.com/aimclub/FEDOT) frameworks.
