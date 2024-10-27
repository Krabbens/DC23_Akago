# DC23_Akago

## Running

To run a Python script, enter any of the following commands. For a command to run successfully, the project needs to be set-up. Refer to the [**Setup**](#setup) section for more information.

-   Upload `dane.md` to your Google Drive: `uv run gdrive.py`.

## Setup

This project uses the [`uv`][uv] project manager. You need to install it to be able to properly run scripts from this project. Please see the [official documentation](https://docs.astral.sh/uv/getting-started/installation/) for installation guide.

Once `uv` is installed, run `uv sync` to update the environment.

### Google Drive

To be able to upload files to your Google Drive, you need to create a test application in your Google account. To do that, follow these steps:

1. In the [Google Cloud console](https://console.cloud.google.com/flows/enableapi?apiid=drive.googleapis.com), create a new project and enable the Google Drive API.
1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
1. Create a new consent screen of type **External**.
1. In the **Edit app registration** form, in the **OAuth consent screen** section, fill in the required fields by providing any application name and user e-mails of your choosing.
1. Skip the **Scopes** section.
1. In the **Test users** section add your e-mail to the list of test users.
1. Confirm everything in the **Summary** section and click **Back to Dashboard**.
1. Go to [Credentials](https://console.cloud.google.com/apis/credentials).
1. Click **Create Credentials** and select **OAuth client ID**.
1. Choose **Desktop app** as the application type.
1. Provide any name for the application and create the OAuth client by clicking **Create**.
1. A popup should appear with the client credentials. Download the credentials in the JSON format.
1. Move the downloaded JSON file to the project root directory and rename it to `credentials.json`.

### VS Code

This project uses [Ruff] for linting and code formatting. To integrate it with VS Code, create a new file `.vscode/settings.json` at the top level with the following content:

```json
{
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.fixAll": "explicit",
            "source.organizeImports": "explicit"
        },
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true
    }
}
```

For integration guides for other code editors, please refer to the [official documentation](https://docs.astral.sh/ruff/editors/).

[uv]: https://docs.astral.sh/uv/ "An extremely fast Python package and project manager, written in Rust."
[Ruff]: https://docs.astral.sh/ruff/ "An extremely fast Python linter and code formatter, written in Rust."
