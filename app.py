from __init__ import create_app

app = create_app()

@app.route('/health')
def health_check():
    # Perform any necessary checks here
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True)