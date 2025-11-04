"""Fix models.py to handle Ollama API response correctly"""

from pathlib import Path

backend_dir = Path(__file__).parent
models_file = backend_dir / "file_organizer" / "models.py"

with open(models_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the problematic line
old_code = "model_names = [m['name'] for m in available_models['models']]"
new_code = """model_names = []
        if 'models' in available_models:
            for m in available_models['models']:
                if isinstance(m, dict) and 'name' in m:
                    model_names.append(m['name'])
                elif isinstance(m, dict) and 'model' in m:
                    model_names.append(m['model'])
                elif hasattr(m, 'name'):
                    model_names.append(m.name)
                elif hasattr(m, 'model'):
                    model_names.append(m.model)"""

content = content.replace(old_code, new_code)

with open(models_file, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Fixed models.py")
print("Restart your backend: python main.py")
