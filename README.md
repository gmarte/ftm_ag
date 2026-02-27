# Django SaaS Platform

This is a Django Backend SaaS project designed to be easily deployed via Railway and Docker. 

## Deployment Guide (Railway)

The codebase is pre-configured to be deployed natively on [Railway](https://railway.app/). We use a Dockerfile to package the application and a `railway.toml` for Railway-specific build and start configurations.

### Prerequisites
1. A GitHub account
2. A Railway account linked to your GitHub
3. Your code pushed to a GitHub repository (like `main` or `master` branch)

### Step-by-step Deployment

1. **Create a new Project on Railway**
   - Head over to your Railway Dashboard.
   - Click **+ New Project**.
   - Select **Deploy from GitHub repo**.
   - Choose this repository from the list. 
   - Add a PostgreSQL Database when asked, or add it later by doing **+ New -> Database -> Add PostgreSQL**.

2. **Configure Environment Variables**
   Once the repository and the database are deployed, you need to set up Environment Variables for the application so it can run securely and successfully connect to the database.

   Navigate to your application's settings and find the **Variables** tab. You need to set the following:

   - `DJANGO_SECRET_KEY`: A strong, random 50-character string.
   - `DJANGO_DEBUG`: Set to `0` or `False` for production.
   - `PORT`: (Optional, Railway sets this by default to `8000`).
   - `DATABASE_URL`: Your PostgreSQL database URL (if you deployed the Postgres plugin, you can reference it using Railway's reference variables like `${{Postgres.DATABASE_URL}}`).

   **Optional Variables** (depended on your setup):
   - Stripe API Keys (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`)
   - Any other external API keys you may be using.

3. **Deploying the Application**
   - The project is configured with `railway.toml` and a custom `Dockerfile`. Railway will automatically build the environment using Python `3.12-slim-bullseye`.
   - The `Dockerfile` installs all dependencies, downloads vendor files, runs `collectstatic`, and runs the application through Gunicorn via the `paracord_runner.sh` script.
   - Migrations (`python manage.py migrate --no-input`) are automatically handled on every deployment start thanks to the script.

4. **Add a Custom Domain**
   - Go to the **Settings** tab of your deployed application inside Railway.
   - Find the **Networking** section.
   - Click **Generate Domain**, or **Custom Domain** if you have your own domain. 

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/gmarte/ftm_ag.git
   cd django_saas
   ```

2. **Create a virtual environment and activate it:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   - Create a `.env` or `.env.dev` file inside your workspace.
   - Configure local settings (like an SQLite database, or a local Postgres).
   - *Reminder: Never commit `.env` files to git.*

5. **Run Migrations and the Server:**
   ```bash
   cd src
   python manage.py migrate
   python manage.py runserver
   ```
