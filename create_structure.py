import os

# Определяем структуру проекта
PROJECT_STRUCTURE = {
    "anonymous_chat": [
        "app.py",
        "config.py",
        "requirements.txt",
        {"models": ["__init__.py", "user.py", "chat.py", "message.py"]},
        {"routes": ["__init__.py", "auth.py", "chat.py"]},
        {"sockets": ["__init__.py", "chat.py"]},
        "static",
        "templates",
        "migrations",
        "utils"
    ]
}

def create_structure(base_path, structure):
    for item in structure:
        if isinstance(item, dict):
            for folder, files in item.items():
                folder_path = os.path.join(base_path, folder)
                os.makedirs(folder_path, exist_ok=True)
                create_structure(folder_path, files)
        else:
            file_path = os.path.join(base_path, item)
            if "." in item:  # Проверяем, что это файл
                with open(file_path, "w") as f:
                    f.write("")
            else:  # Иначе создаем папку
                os.makedirs(file_path, exist_ok=True)

def main():
    base_path = os.getcwd()
    create_structure(base_path, PROJECT_STRUCTURE["anonymous_chat"])
    print("Структура проекта успешно создана!")

if __name__ == "__main__":
    main()
