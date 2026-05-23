#!/bin/bash

set -e

if [ -z "$1" ]; then
  echo "❌ Error: No app name provided."
  echo "👉 Usage: ./create_app.sh <app_name>"
  echo "💡 Example: ./create_app.sh employee"
  exit 1
fi

APP_NAME=$1
APP_CLASS_NAME="$(tr '[:lower:]' '[:upper:]' <<< ${APP_NAME:0:1})${APP_NAME:1}"

BASE_DIR="apps/$APP_NAME"

echo "🚀 Bootstrapping DDD structure for: $APP_NAME..."

mkdir -p "$BASE_DIR"
touch "$BASE_DIR/__init__.py"

cat <<EOF > "$BASE_DIR/apps.py"
from django.apps import AppConfig

class ${APP_CLASS_NAME}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.${APP_NAME}'
EOF

cat <<EOF > "$BASE_DIR/urls.py"
from django.urls import path

app_name = '$APP_NAME'

urlpatterns = [
    # path('', views.${APP_NAME}_views.YourAPIView.as_view(), name='example'),
]
EOF

# --- NEW: Handle migrations directory separately ---
mkdir -p "$BASE_DIR/migrations"
touch "$BASE_DIR/migrations/__init__.py"
# ---------------------------------------------------

DIRECTORIES=(
    "admin" 
    "models" 
    "views" 
    "services" 
    "selectors" 
    "serializers" 
    "tasks" 
    "tests" 
    "documentations" 
    "filters" 
    "functions"
)

for dir in "${DIRECTORIES[@]}"; do
    TARGET_DIR="$BASE_DIR/$dir"
    
    mkdir -p "$TARGET_DIR"
    touch "$TARGET_DIR/__init__.py"
    
    FILE_NAME="${APP_NAME}_${dir}.py"
    touch "$TARGET_DIR/$FILE_NAME"
    
    echo "\"\"\"$dir module for $APP_NAME.\"\"\"" > "$TARGET_DIR/$FILE_NAME"
done

echo "✅ Successfully generated the '$APP_NAME' app structure in $BASE_DIR/"
echo "⚠️  Next step: Add 'apps.$APP_NAME' to LOCAL_APPS in config/settings/base.py"