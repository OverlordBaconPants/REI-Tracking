import secrets
import os
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key and save it to .env file."""
    # Generate a secure secret key
    secret_key = secrets.token_hex(32)
    
    # Path to .env file
    env_path = Path('.env')
    
    # Read existing .env content
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Remove existing SECRET_KEY if present
    lines = [line for line in lines if not line.startswith('SECRET_KEY=')]
    
    # Add new SECRET_KEY
    lines.append(f'SECRET_KEY={secret_key}\n')
    
    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(lines)
    
    print(f"Generated new secret key and saved to .env file")
    print(f"Secret key: {secret_key}")

if __name__ == '__main__':
    generate_secret_key()