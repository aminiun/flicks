from kavenegar import KavenegarAPI


def send_sms_template(receptor, template, token, token2=None, token3=None):
    """

    :param receptor: phone number
    :type receptor: str - phone number
    :param template: sms template (kavenegar)
    :type template: str
    :param token: %token
    :type token: str
    :param token2: %token2
    :type token2: str
    :param token3: %token3
    :type token3: str
    :return: kavenegar response
    :rtype: json
    """
    try:
        api = KavenegarAPI(KAVENEGAR_AUTH_TOKEN)
        params = {
            'receptor': str(receptor),
            'template': template
            }
        if token:
            params.update({'token': sms_character_replace(token)})
        if token2:
            params.update({'token2': sms_character_replace(token2)})
        if token3:
            params.update({'token3': sms_character_replace(token3)})
        response = api.verify_lookup(params)
        print(str(response))  # todo add logger
        return response
    except APIException as api_exception:  # pragma: no cover
        print(str(api_exception))  # todo add logger
        return api_exception
