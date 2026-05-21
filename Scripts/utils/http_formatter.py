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

    formatted = format_http_response(headers[0], headers[1:], body)
    redirects = response.get('redirects') or []

    if not redirects:
        return formatted

    redirect_lines = [
        '',
        'Redirects'
    ]

    for status_code, source_url, target_url in redirects:
        redirect_lines.append(f'  HTTP {status_code}: {source_url} -> {target_url}')

    if response.get('final_url'):
        redirect_lines.append(f'  Final URL: {response["final_url"]}')

    return formatted + '\n' + '\n'.join(redirect_lines)


def format_requests_response(response):
    formatted = format_http_response(
        f'HTTP {response.status_code}',
        response.headers,
        response.text
    )

    if not response.history:
        return formatted

    redirect_lines = [
        '',
        'Redirects'
    ]

    for item in response.history:
        redirect_lines.append(f'  HTTP {item.status_code} -> {item.headers.get("Location", item.url)}')

    redirect_lines.append(f'  Final URL: {response.url}')

    return formatted + '\n' + '\n'.join(redirect_lines)