def prepare_response(success: bool, message: str, data: dict = None):
    response = {'success': success, 'message': message}
    if data:
        if '_id' in data:
            data.pop('_id')
        response['data'] = data
    return response

