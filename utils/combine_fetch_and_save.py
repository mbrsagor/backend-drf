def sync_external_data():
    data = fetch_external_api_data()
    save_data_to_database(data)

