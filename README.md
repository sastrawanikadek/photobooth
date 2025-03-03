# Photobooth

[![Python](https://img.shields.io/badge/Python-3471A2?style=flat&logo=python&logoColor=white)](https://python.org/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react&logoColor=61DAFB)](https://react.dev/)
[![Typescript](https://img.shields.io/badge/TypeScript-007ACC?style=flat&logo=typescript&logoColor=white)](https://typescriptlang.org/)
[![Electron](https://img.shields.io/badge/Electron-20232A?style=flat&logo=electron&logoColor=86C3D0)](https://electronjs.org/)

Desktop application for a photobooth system to capture wonderful moments 📸

Photobooth consists of the server and client parts, the server is built with [Python](https://python.org) and utilizing [Asyncio](https://docs.python.org/3/library/asyncio.html) to enable asynchronous programming. The client part which is the desktop app is built with [React](https://react.dev/) and [Typescript](https://typescriptlang.org/) on [Electron](https://electronjs.org/) ecosystem.

## Getting Started

Here are the instructions for setting up and running the application locally.

### Prerequisites

There are things that you need to install first in your local machine:

- Python 3.10 or higher
- Node.js 20.11.1 or higher
- Git
- Yarn

For installing the Python and Node.js, we recommend using [pyenv](https://github.com/pyenv/pyenv) and [nvm](https://github.com/nvm-sh/nvm) to manage your Python and Node.js version.

We also recommend you to use [Visual Studio Code](https://code.visualstudio.com/download) as the text editor because we already provide list of extensions that you can install and convenient tasks that you can run to make your life easier.

### Installation

You need to follow these steps to setup the project:

1. Clone the repository

   ```bash
   git clone https://github.com/sastrawanikadek/photobooth.git
   cd photobooth
   ```

   Clone the repository using git and open it in your favorite text editor. You can skip step 2 and 3 if you already installed the correct Python and Node.js version.

2. Install Python version

   The project use Python 3.10 but you can use the higher version if you want. If you already install the [pyenv](https://github.com/pyenv/pyenv), it's easy to switch between the versions. We already provide the `.python-version` file so you just need to run these command on your terminal inside the project directory.

   ```bash
   pyenv install
   python --version # Verify the version is correct
   ```

3. Install Node.js version

   Next thing you need is to install the correct Node.js version, the project use Node.js 20.11.1 but feel free to use the higher version. If you already install [nvm](https://github.com/nvm-sh/nvm), the step is similar as the previous step, just run these command on your terminal inside the project directory.

   ```bash
   nvm install
   nvm use
   node --version # Verify the version is correct
   ```

4. Install dependencies

   You can install all the necessary dependencies by running this command on your terminal inside the project directory.

   ```bash
   source scripts/setup.sh
   ```

   Or you can also open the command palette and run the "Tasks: Run Task" command, and select the "Setup" task if you're using [Visual Studio Code](https://code.visualstudio.com/download).

### Running the Application

Because the application is separated into two parts, you need to run each part separately. Here are some steps to do it:

1. Run the client

   To run the client or the frontend part, you just need to run this command in your terminal.

   ```bash
   yarn start
   ```

   Or if you're using [Visual Studio Code](https://code.visualstudio.com/download), you can also open the command palette and run the "Tasks: Run Task" command, and select the "Start Client" task.

   This will start the client side and new electron window should be showing up.

2. Run the server

   Before you can run the server or the backend part, you need to migrate the database first. Just run this command on your terminal.

   ```bash
   source .venv/bin/activate # Activate virtual environment
   alembic upgrade head
   ```

   Or if you're using [Visual Studio Code](https://code.visualstudio.com/download), you can also open the command palette and run the "Tasks: Run Task" command, and select the "Migrate Database" task.

   Verify that `database.db` file is exists on the root of the project directory, the next step is to run this command so the server can start.

   ```
   watchmedo auto-restart --pattern "*.py" --recursive --signal SIGTERM -- python3 -m server.main
   ```

   Or if you're using [Visual Studio Code](https://code.visualstudio.com/download), you can also open the command palette and run the "Tasks: Run Task" command, and select the "Start Server" task.

   You can access the server on http://localhost:8080.

## Tasks

Here are some tasks that you can run from the command palette in [Visual Studio Code](https://code.visualstudio.com/download).

- **Setup**

  Run the setup script, this will create a Python virtual environment if it's not exists and install the necessary dependencies to be able to start both the client and server.

- **Start Client**

  Running the client/frontend part of the application.

- **Start Server**

  Running the server/backend part of the application. You can access it on http://localhost:8080.

- **Migrate Database**

  Create all the tables in the database.
