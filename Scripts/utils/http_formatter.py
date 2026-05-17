def format_http_response(status, headers=None, body=''):
    formatted = [
        'Status',
        f'  {status}',
        '',
        'Headers'
    ]

    if headers:
        if hasattr(headers, 'items'):
            formatted.extend(f'  {key}: {value}' for key, value in headers.items())
        else:
            formatted.extend(f'  {header}' for header in headers)
    else:
        formatted.append('  No headers')

    formatted.extend([
        '',
        'Body',
        body or ''
    ])

    return '\n'.join(formatted)


def format_parsed_response(response):
    headers = response.get('headers', '').splitlines()
    body = response.get('body', '')

    if not headers:
        return body

    return format_http_response(headers[0], headers[1:], body)


def format_requests_response(response):
    return format_http_response(
        f'HTTP {response.status_code}',
        response.headers,
        response.text
    )